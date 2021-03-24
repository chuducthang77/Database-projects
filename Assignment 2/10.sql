.print Question 10 - thang

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