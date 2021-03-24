.print Question 5 - thang

select posts.poster
from questions, posts
where questions.pid = posts.pid

intersect

select posts.poster
from answers, posts
where answers.pid = posts.pid

intersect
 
select posts.poster
from votes, posts
where votes.pid = posts.pid
group by posts.poster 
having count(votes.vno) > 4;
