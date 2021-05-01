create sequence rowidseq start 1;

create table block (
                rowid bigint default nextval('rowidseq') not null; 
                p int not null,
                q int not null,
                x int not null,
                y int not null,
                z int not null,
                w int not null
);
create unique index block_pqxyz_idx on block (p, q, x, y, z);

create table if not exists light (
                p int not null,
                q int not null,
                x int not null,
                y int not null,
                z int not null,
                w int not null
);
create unique index light_pqxyz_idx on light (p, q, x, y, z);

create table if not exists sign (
                p int not null,
                q int not null,
                x int not null,
                y int not null,
                z int not null,
                face int not null,
                text text not null
            );
create index sign_pq_idx on sign (p, q);
create unique index sign_xyzface_idx on sign (x, y, z, face);

create table block_history (
               timestamp real not null,
               user_id int not null,
               x int not null,
               y int not null,
               z int not null,
               w int not null
            );
