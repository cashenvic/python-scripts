create table products
(
    id               INT PRIMARY KEY auto_increment,
    product_id       varchar(128),
    url              varchar(255),
    title            varchar(255),
    price            varchar(128),
    promo_price      varchar(128),
    full_description longtext,
    images_urls      text
);
