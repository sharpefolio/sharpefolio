CREATE  TABLE `prices` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `stock_id` INT UNSIGNED NOT NULL ,
  `date` date NOT NULL ,
  `closing_price` double(10,4) UNSIGNED NOT NULL ,
  `change` double(14,8) NOT NULL DEFAULT 0 ,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_price` (`stock_id`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `stocks` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `symbol` varchar(50) NOT NULL,
  `company` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_symbol` (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `reports` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `duration` INT UNSIGNED NOT NULL,
  `formula` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_report` (`date`, `duration`, `formula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ratios` (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `stock_id` INT UNSIGNED NOT NULL,
  `report_id` INT UNSIGNED NOT NULL,
  `ratio` double(10,6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_stock_report` (`stock_id`, `report_id`),
  KEY `ratio` (`ratio`),
  KEY `report_id` (`report_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `picks` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `recipe_id` INT UNSIGNED NOT NULL,
  `report_id` INT UNSIGNED NOT NULL,
  `stock_id` INT UNSIGNED NOT NULL,
  `gain` double(10,6),
  `weight` double(10,6) UNSIGNED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_recipe_stock` (`recipe_id`, `stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipes` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `n_stocks` INT UNSIGNED NOT NULL,
  `check_correlation` tinyint(1) UNSIGNED NOT NULL,
  `distribution` varchar(10),
  `report_duration` INT UNSIGNED NOT NULL,
  `report_formula` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `yahoo_sync_logs` (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `stock_id` INT UNSIGNED NOT NULL,
  `year` INT UNSIGNED NOT NULL,
  `month` INT UNSIGNED NOT NULL,
  `is_successful` TINYINT(1) UNSIGNED NOT NULL,
  `log` TEXT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_stock_month_log` (`stock_id`, `year`, `month`),
  KEY `is_successful` (`is_successful`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `benchmarks` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `symbol` varchar(50) NOT NULL,  
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_symbol` (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `benchmarks` (`id`, `symbol`, `name`)
VALUES
  (1, '^GSPC', 'S&P 500'),
  (2, '^TNX', '10-year U.S. Treasury Bonds');

CREATE TABLE `benchmark_prices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `benchmark_id` int(11) unsigned NOT NULL,
  `date` date NOT NULL,
  `closing_price` double(10,4) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_price` (`stock_id`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

