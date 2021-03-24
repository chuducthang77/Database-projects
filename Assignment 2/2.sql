.print Question 2 - thang

SELECT questions.pid, posts.title
FROM posts, questions, tags t1, tags t2
WHERE t1.pid = posts.pid
AND t2.pid = posts.pid
AND questions.pid = posts.pid
AND lower(t1.tag) LIKE '%database%'
AND lower(t2.tag) LIKE '%relational%'

UNION

SELECT questions.pid, posts.title
FROM posts, questions
WHERE posts.pid = questions.pid
AND lower(posts.title) LIKE '%relational database%';
