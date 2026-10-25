import {sqliteTable,text,integer} from 'drizzle-orm/sqlite-core';
export const responses=sqliteTable('responses',{rater:text('rater').primaryKey(),materialsHash:text('materials_hash').notNull(),mode:text('mode').notNull(),payload:text('payload').notNull(),payloadHash:text('payload_hash').notNull(),isTest:integer('is_test').notNull().default(0),receivedAt:text('received_at').notNull()});
