-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC;

-- Q2 average latency per intent
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC;

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) AS negative_feedback_count
FROM interaction i
JOIN feedback f ON f.request_id = i.request_id
WHERE f.rating = -1
GROUP BY i.topic
ORDER BY negative_feedback_count DESC;

-- H2: What share of answers used a backup / degraded path?
-- Question: What share of answers used a backup (degraded) path?
SELECT 
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    COUNT(*) AS total_count,
    ROUND(100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS degraded_pct
FROM interaction;
/*
Result:
degraded_count | total_count | degraded_pct
---------------+-------------+-------------
38             | 300         | 12.67
*/
