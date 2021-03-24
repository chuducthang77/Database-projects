.print Question 6 - thang

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