.print Question 3 - thang

select questions.pid, posts.title
from questions, posts
where questions.pid = posts.pid

except

select questions.pid, p2.title
from questions, answers, posts p1, posts p2
where questions.pid = answers.qid 
and answers.pid = p1.pid
and questions.pid = p2.pid
and datetime(p1.pdate) <= datetime(p2.pdate, '+3 days');