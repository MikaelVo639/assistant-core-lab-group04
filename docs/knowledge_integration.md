# Knowledge integration

The knowledge module provides the directory and handbook interfaces consumed by AssistantService.
Its merged implementation and tests are retained from PR #3, with additional validation regressions.

## Public interfaces

- OfficeDirectory accepts a dictionary, CSV path or data directory; from_csv(path) is the factory used by the CLI.
- names returns a defensive name set; offices returns a defensive record list; file_path exposes the source path.
- find(text) returns Office or None. lookup is a compatible alias; lookup_formatted returns the office display text.
- Office is a frozen record with name, room and hours; format_response formats these values.
- Handbook accepts a Rule list, JSON path or data directory; from_json(path) is the CLI factory.
- The existing offices= and rules= constructor keywords remain supported alongside target=.
- rules returns a defensive list; file_path exposes the source path; search(query) returns Rule or None.
- search_match(query) wraps a result in RuleMatch with its score and delegated rule fields.
- Rule exposes id, title, text and a Source property; HandbookRule is a compatibility alias.
- Rule and Handbook provide formatted fallback helpers that preserve the source ID.

## Validation and search

Missing, empty, malformed or unreadable data raises DataError at startup. Duplicate office names and rule IDs are rejected.
CSV fields are read by header name, allowing reordered required columns and extra metadata columns.
Search and RuleMatch scores share normalized keyword tokens longer than three characters; ties preserve input order.
Runtime composition and error behavior are documented in docs/architecture.md.
