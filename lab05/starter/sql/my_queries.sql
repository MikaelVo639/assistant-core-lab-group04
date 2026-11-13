-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent;

-- Q2 average latency per intent
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY intent;

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) AS thumbs_down
FROM interaction AS i
JOIN feedback AS f ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic;

-- H2: Which intents had unresolved requests, and how many?
SELECT intent, COUNT(*) AS unresolved_requests
FROM interaction
WHERE resolved = 0
GROUP BY intent
ORDER BY unresolved_requests DESC, intent;

-- H2 result on 300 seeded interactions (intent, unresolved_requests):
-- ('unknown', 26)

-- H2: What share of answers used a backup (degraded) path?
SELECT
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    COUNT(*) AS total_count,
    ROUND(100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS degraded_pct
FROM interaction;

-- H2 result on 300 seeded interactions (degraded_count, total_count, degraded_pct):
-- (38, 300, 12.67)
