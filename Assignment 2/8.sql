.print Question 8 - thang

select
    E.poster,
    ifnull(A.pid_ques,0),
    ifnull(B.pid_ans,0),
    ifnull(C.pid_cast,0),
    ifnull(D.total,0)
from (
    select distinct A.poster from (select posts.poster, count(questions.pid) as pid_ques -- for each user, total number of q
from posts, questions
where posts.pid = questions.pid
group by posts.poster) A
    union
    select distinct B.poster from (select posts.poster, count(answers.pid) as pid_ans -- for each user, total number of q
from posts, answers
where posts.pid = answers.pid
group by posts.poster) B
    union
    select distinct C.uid from (select votes.uid, count(*) as pid_cast -- for each user, total number of casted votes
from votes
group by votes.uid) C
    union
    select distinct D.poster from (select t1.poster, sum(num) as total from ( -- for each user, total number of received votes
select posts.poster, votes.pid, count(votes.vno) as num
from votes, posts
where votes.pid = posts.pid
group by votes.pid ) t1
group by t1.poster) D
) as E
    left outer join (select posts.poster, count(questions.pid) as pid_ques -- for each user, total number of q
from posts, questions
where posts.pid = questions.pid
group by posts.poster) A on A.poster = E.poster
    left outer join (select posts.poster, count(answers.pid) as pid_ans -- for each user, total number of q
from posts, answers
where posts.pid = answers.pid
group by posts.poster) B on B.poster = E.poster
    left outer join (select votes.uid, count(*) as pid_cast -- for each user, total number of casted votes
from votes
group by votes.uid) C on C.uid = E.poster
    left outer join (select t1.poster, sum(num) as total from ( -- for each user, total number of received votes
select posts.poster, votes.pid, count(votes.vno) as num
from votes, posts
where votes.pid = posts.pid
group by votes.pid ) t1
group by t1.poster) D on D.poster = E.poster;