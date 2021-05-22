create table submissions
(
	id bigserial not null,
	submission_id varchar not null,
	created_utc timestamptz not null,
	title varchar not null
);

create unique index submissions_id_uindex
	on submissions (id);

alter table submissions
	add constraint submissions_pk
		primary key (id);

