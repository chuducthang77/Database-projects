.print Question 9 - thang

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