.print Question 1 - thang

SELECT Distinct users.uid
FROM users, badges, ubadges, posts, questions
WHERE users.uid = ubadges.uid
AND badges.bname = ubadges.bname
AND badges.type = 'gold'
AND posts.poster = users.uid
AND  posts.pid = questions.pid;