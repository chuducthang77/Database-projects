.print Question 4 - thang

select p1.poster
from posts p1, posts p2, answers
where p1.pid = answers.pid
and p2.pid = answers.qid
and p1.poster = p2.poster
group by p1.poster
having count(p2.poster) > 2

INTERSECT

select posts.poster
from questions, posts
where questions.pid = posts.pid
group by posts.poster
having count(questions.pid) > 2;  