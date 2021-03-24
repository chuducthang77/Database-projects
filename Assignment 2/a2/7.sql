.print Question 7 - thang

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