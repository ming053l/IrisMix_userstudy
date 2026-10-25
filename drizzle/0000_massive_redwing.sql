CREATE TABLE `responses` (
	`rater` text PRIMARY KEY NOT NULL,
	`materials_hash` text NOT NULL,
	`mode` text NOT NULL,
	`payload` text NOT NULL,
	`payload_hash` text NOT NULL,
	`is_test` integer DEFAULT 0 NOT NULL,
	`received_at` text NOT NULL
);
