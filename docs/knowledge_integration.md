# Knowledge Module Integration Guide

This document outlines the design, public interfaces, and integration details for the `knowledge.py` module developed by **Đăng** for the `assistant_core` package.

---

## 1. Components Implemented

### Module: `src/assistant_core/knowledge.py`

#### A. Data Models
1. **`Office`** (Dataclass):
   - **Attributes**: `name: str`, `room: str`, `hours: str`
   - **Methods**:
     - `format_response() -> str`: Formats the office information for user display matching monolith output:
       `"{name}: room {room}, open {hours}"`.

2. **`Rule`** (Dataclass, alias: `HandbookRule`):
   - **Attributes**: `id: str`, `title: str`, `text: str`
   - **Properties**:
     - `source -> Source`: Returns a `Source(id=self.id, title=self.title)` instance.
   - **Methods**:
     - `format_fallback_response() -> str`: Returns fallback formatted string with source citation:
       `"{text} (source: {id})"`.

3. **`RuleMatch`** (Dataclass):
   - Wraps a `Rule` with its keyword matching `score: int`. Provides direct delegated properties for `id`, `title`, `text`, `source`, and `format_fallback_response()`.

---

#### B. `OfficeDirectory` Class
Manages university office directory records loaded from CSV.

- **Constructors**:
  - `OfficeDirectory(target: dict[str, Office] | Path | str)`: Accepts either a dictionary of offices, a CSV file path (`Path` or `str`), or a data directory containing `offices.csv`.
  - `OfficeDirectory.from_csv(path: Path | str) -> OfficeDirectory`: Factory method conforming to the Lab 3 manual.
- **Properties**:
  - `names -> set[str]`: Set of all lowercase office names (used directly by `router.py` to identify office intent).
  - `offices -> list[Office]`: List of all loaded `Office` objects.
  - `file_path -> Path | None`: Resolved CSV path if loaded from file.
- **Query Methods**:
  - `find(text: str) -> Office | None`: Finds matching office by keyword search across the query text (case-insensitive).
  - `lookup(query: str) -> Office | None`: Alias for `find()`.
  - `lookup_formatted(query: str) -> str | None`: Finds office and returns the formatted string, or `None`.
- **Validation & Exceptions**:
  - Raises `DataError` if the CSV file is missing, empty, has invalid headers (`name,room,hours`), or contains malformed rows.

---

#### C. `Handbook` Class
Manages student handbook rules loaded from JSON and handles regulation search.

- **Constructors**:
  - `Handbook(target: list[Rule] | Path | str)`: Accepts either a list of `Rule` instances, a JSON file path, or a data directory containing `handbook.json`.
  - `Handbook.from_json(path: Path | str) -> Handbook`: Factory method conforming to the Lab 3 manual.
- **Properties**:
  - `rules -> list[Rule]`: List of all loaded rules.
  - `file_path -> Path | None`: Resolved JSON path if loaded from file.
- **Search Methods**:
  - `search(query: str) -> Rule | None`: Searches for rules matching query words longer than 3 characters. Returns the highest-scoring `Rule` if `score >= 1`, or `None`.
  - `search_match(query: str) -> RuleMatch | None`: Same as `search()`, but wraps the result in `RuleMatch` containing the matching `score`.
  - `search_formatted_fallback(query: str) -> str | None`: Searches and returns the deterministic fallback text with citation.
- **Validation & Exceptions**:
  - Raises `DataError` if the file is missing, JSON syntax is invalid, root is not a list, is empty, or items miss required keys (`id`, `title`, `text`).

---

## 2. Temporary Stubs Provided for the Team

To allow independent testing without waiting for peer commits:

1. **`src/assistant_core/errors.py`**:
   - Defined base domain exceptions: `AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError`.
   - *For Thắng*: You can extend or add docstrings/attributes to this file without breaking `DataError`.

2. **`src/assistant_core/models.py`**:
   - Defined: `Source`, `Intent`, `Message`, `Response`.
   - *For Thắng*: You can refine field validation rules or helpers.

---

## 3. Teammate Integration Guide

### For Đạt (`config.py` / `Settings`):
`Settings` provides `data_dir: Path = Path("data")`. Both `OfficeDirectory` and `Handbook` accept `settings.data_dir` directly:
```python
from assistant_core.knowledge import Handbook, OfficeDirectory

# Passing data_dir directly resolves 'offices.csv' and 'handbook.json' automatically:
office_directory = OfficeDirectory.from_csv(settings.data_dir)
handbook = Handbook.from_json(settings.data_dir)
```

### For Thịnh (`router.py` / `Router`):
Use `office_directory.names` (`set[str]`) for routing queries:
```python
def route(text: str, office_names: set[str]) -> Intent:
    t = text.lower().strip()
    if any(name in t for name in office_names):
        return Intent.OFFICE
    # ...
```

### For Minh (`service.py` / `AssistantService`):
Inject instances into `AssistantService`:
```python
class AssistantService:
    def __init__(self, settings, offices: OfficeDirectory, handbook: Handbook, responder):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder

    def handle(self, msg: Message) -> Response:
        intent = route(msg.text, self.offices.names)
        if intent == Intent.OFFICE:
            office = self.offices.find(msg.text)
            return Response(answer=office.format_response(), intent=intent)
        elif intent == Intent.RULE:
            rule = self.handbook.search(msg.text)
            if not rule:
                return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)
            sources = [Source(id=rule.id, title=rule.title)]
            try:
                answer = self.responder.explain(msg.text, rule)
                return Response(answer=answer, intent=intent, sources=sources)
            except ProviderError:
                return Response(
                    answer=rule.format_fallback_response(),
                    intent=intent,
                    sources=sources,
                    degraded=True,
                )
```

---

## 4. Test Suite Coverage (`tests/test_knowledge.py`)

20 unit tests verify:
- Ingestion of production data from `data/` using `from_csv` and `from_json`.
- Keyword search and case insensitivity.
- Response formatting and fallback citations.
- Returning `None` for unmatched queries.
- Strict error handling with `DataError` on:
  - Missing file paths.
  - Empty files.
  - Invalid CSV headers or row columns.
  - Corrupt JSON, non-list root, or missing fields (`id`, `title`, `text`).
