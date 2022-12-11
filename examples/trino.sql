create schema hive.raw with (location = 's3a://raw/')

create schema delta.transformed with (location = 's3a://transformed/')

create table hive.raw.customers 
( id integer,
  first_name varchar,
  last_name varchar
) with (
external_location = 's3a://raw/jaffle_shop_customers',
format = 'parquet'
)

create table hive.raw.orders
( id integer,
  user_id integer,
  order_date varchar,
  status varchar
) with (
external_location = 's3a://raw/jaffle_shop_orders',
format = 'parquet'
)

select * from hive.raw.customers

select * from hive.raw.orders 

select * from hive.raw.payments 

select * from delta.transformed.test_delta

select * from iceberg.transformed.test_iceberg
