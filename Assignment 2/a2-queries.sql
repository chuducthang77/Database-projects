.echo on
--Question 1
SELECT Distinct users.uid
FROM users, badges, ubadges, posts, questions
WHERE users.uid = ubadges.uid
AND badges.bname = ubadges.bname
AND badges.type = 'gold'
AND posts.poster = users.uid
AND  posts.pid = questions.pid;

--Question 2

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

--Question 3

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

--Question 4

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

--Question 5
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

--Question 6
select A.tag, B.pcnt, A.cnt
    from
    (select tags.tag, count(votes.vno) as cnt
    from votes, tags
    where tags.pid = votes.pid
    group by tags.tag
    order by cnt desc
    limit 3) A
left join
    (select tags.tag, count(posts.pid) as pcnt
    from tags, posts
    where tags.pid = posts.pid
    group by tags.tag) B
on A.tag = B.tag;

--Question 7
select A.pdate, A.tag, A.cnt
    from 
    (select posts.pdate, tags.tag, count(tags.pid) as cnt 
    from tags, posts
    where tags.pid = posts.pid
    group by posts.pdate, tags.tag
    order by posts.pdate, cnt desc) A, 
    (select C.pdate, max(C.cnt) as cnt
    from ( select posts.pdate, tags.tag, count(tags.pid) as cnt
            from tags, posts
            where tags.pid = posts.pid
            group by posts.pdate, tags.tag
            order by posts.pdate, cnt desc
            ) as C
    group by C.pdate) B
where A.pdate == B.pdate 
and A.cnt == B.cnt;

--Question 8

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

--Question 9
Create view questionInfo(pid, uid, theaid, voteCnt, ansCnt)
as select A.pid, A.poster, A.theaid, ifnull(B.num,0), ifnull(C.cnt, 0)
from (select questions.pid, posts.pdate, posts.poster, questions.theaid
        from questions, posts
        where questions.pid = posts.pid
        and date(posts.pdate) >= date('now', '-1 month')) A 
    left join 
    (select votes.pid, count(*) as num
        from votes, questions
        where votes.pid = questions.pid
        group by votes.pid) B 
    ON A.pid = B.pid
    left join 
    (select answers.qid, count(*) as cnt
    from answers
    group by answers.qid) C 
    ON A.pid = C.qid;


--Question 10
select A.city, ifnull(A.cnt,0), ifnull(B.ucnt,0), ifnull(C.qcnt * 1.0 /A.cnt,0), ifnull(D.total,0)  -- for each city, number of ques/ users
from 
    (select users.city, count(*) as cnt 
    from users
    group by users.city) A 
    left join 
    (select users.city, count(ubadges.uid) as ucnt
    from ubadges, badges, users
    where ubadges.bname = badges.bname
    and badges.type = 'gold'
    and ubadges.uid = users.uid
    group by users.city) B
    On A.city = B.city
    left join
    (select users.city, count(questionInfo.pid) as qcnt
    from users, posts, questionInfo
    where users.uid = posts.poster
    and posts.pid = questionInfo.pid
    group by users.city) C
    On A.city = C.city
    left join
    (select A.city, sum(A.cnt) as total
    from ( select users.city, count(votes.vno) as cnt
            from votes, posts, users
            where votes.pid = posts.pid
            and users.uid = posts.poster
            and date(posts.pdate) >= date('now', '-1 month')
            group by votes.pid) A
    group by A.city) D 
    On A.city = D.city;