BEGIN;

-- NovaStore AI - Development Seed Data
-- M1.5 - Seed Data
-- WARNING: Development reset only. DO NOT run against production.

TRUNCATE TABLE
    audit_logs, approvals, tool_calls, agent_runs, document_chunks, documents,
    refunds, tickets, messages, conversations, shipments, payments,
    order_status_history, order_items, orders, inventory, products,
    customers, users
CASCADE;

INSERT INTO users (id,email,password_hash,role,is_active) VALUES
('0e94f508-62ed-4beb-a856-d96f324a4994','mostafa.customer@novastore.local','SEED_HASH_NOT_FOR_PRODUCTION','customer',TRUE),
('76a1912f-8a91-44db-b95c-ff488929d62a','ahmed.customer@novastore.local','SEED_HASH_NOT_FOR_PRODUCTION','customer',TRUE),
('33a0e628-d157-41d2-b089-b50c87fbb454','omar.admin@novastore.local','SEED_HASH_NOT_FOR_PRODUCTION','admin',TRUE),
('aab4d793-8c91-40d1-b183-c2c4a207abbc','sara.support@novastore.local','SEED_HASH_NOT_FOR_PRODUCTION','support_agent',TRUE);

INSERT INTO customers (id,user_id,first_name,last_name,phone) VALUES
('9581cd4f-0f8e-4e04-966f-5d45440c6ef3','76a1912f-8a91-44db-b95c-ff488929d62a','Ahmed','Hassan','+201000000001'),
('407eeb7b-7942-410f-a28e-68287fe0fb14','0e94f508-62ed-4beb-a856-d96f324a4994','Mostafa','Mashaal','+201000000002');

INSERT INTO products (id,sku,name,description,category,price,is_active) VALUES
('11111111-1111-4111-8111-111111111111','NS-LAP-001','NovaBook Pro 15','15-inch performance laptop.','Laptops',1299.99,TRUE),
('22222222-2222-4222-8222-222222222222','NS-LAP-002','NovaBook Air 14','Lightweight 14-inch laptop.','Laptops',899.99,TRUE),
('33333333-3333-4333-8333-333333333333','NS-PHN-001','NovaPhone X1','Flagship smartphone.','Phones',799.99,TRUE),
('44444444-4444-4444-8444-444444444444','NS-PHN-002','NovaPhone Lite','Affordable smartphone.','Phones',399.99,TRUE),
('55555555-5555-4555-8555-555555555555','NS-MON-001','NovaView 27 4K','27-inch 4K monitor.','Monitors',449.99,TRUE),
('66666666-6666-4666-8666-666666666666','NS-MON-002','NovaView 24 FHD','24-inch Full HD monitor.','Monitors',199.99,TRUE),
('77777777-7777-4777-8777-777777777777','NS-ACC-001','Nova Wireless Keyboard','Wireless keyboard.','Accessories',79.99,TRUE),
('88888888-8888-4888-8888-888888888888','NS-ACC-002','Nova USB-C Hub','USB-C connectivity hub.','Accessories',49.99,FALSE);

INSERT INTO inventory (id,product_id,available_quantity,reserved_quantity) VALUES
('90000000-0000-4000-8000-000000000001','11111111-1111-4111-8111-111111111111',10,1),
('90000000-0000-4000-8000-000000000002','22222222-2222-4222-8222-222222222222',19,1),
('90000000-0000-4000-8000-000000000003','33333333-3333-4333-8333-333333333333',15,1),
('90000000-0000-4000-8000-000000000004','44444444-4444-4444-8444-444444444444',30,0),
('90000000-0000-4000-8000-000000000005','55555555-5555-4555-8555-555555555555',8,0),
('90000000-0000-4000-8000-000000000006','66666666-6666-4666-8666-666666666666',23,2),
('90000000-0000-4000-8000-000000000007','77777777-7777-4777-8777-777777777777',39,1),
('90000000-0000-4000-8000-000000000008','88888888-8888-4888-8888-888888888888',0,0);

INSERT INTO orders (id,order_number,customer_id,status,total_amount,created_at,updated_at) VALUES
('a0000000-0000-4000-8000-000000000001','NS-10001','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','processing',899.99,'2026-10-01 10:00:00+03','2026-10-01 10:00:00+03'),
('a0000000-0000-4000-8000-000000000002','NS-10002','407eeb7b-7942-410f-a28e-68287fe0fb14','shipped',1379.98,'2026-10-01 12:00:00+03','2026-10-02 09:00:00+03'),
('a0000000-0000-4000-8000-000000000003','NS-10003','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','in_transit',599.98,'2026-10-02 14:00:00+03','2026-10-03 11:00:00+03'),
('a0000000-0000-4000-8000-000000000004','NS-10004','407eeb7b-7942-410f-a28e-68287fe0fb14','delivered',1299.99,'2026-09-28 09:00:00+03','2026-10-02 16:00:00+03'),
('a0000000-0000-4000-8000-000000000005','NS-10005','407eeb7b-7942-410f-a28e-68287fe0fb14','delivered',449.99,'2026-09-29 10:00:00+03','2026-10-03 15:00:00+03');

INSERT INTO order_items (id,order_id,product_id,quantity,unit_price) VALUES
('b0000000-0000-4000-8000-000000000001','a0000000-0000-4000-8000-000000000001','22222222-2222-4222-8222-222222222222',1,899.99),
('b0000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000002','11111111-1111-4111-8111-111111111111',1,1299.99),
('b0000000-0000-4000-8000-000000000003','a0000000-0000-4000-8000-000000000002','77777777-7777-4777-8777-777777777777',1,79.99),
('b0000000-0000-4000-8000-000000000004','a0000000-0000-4000-8000-000000000003','66666666-6666-4666-8666-666666666666',2,299.99),
('b0000000-0000-4000-8000-000000000005','a0000000-0000-4000-8000-000000000004','11111111-1111-4111-8111-111111111111',1,1299.99),
('b0000000-0000-4000-8000-000000000006','a0000000-0000-4000-8000-000000000005','55555555-5555-4555-8555-555555555555',1,449.99);

-- Correct NS-10003 total to match two monitors at 199.99 each + one keyboard.
UPDATE orders SET total_amount=599.98 WHERE id='a0000000-0000-4000-8000-000000000003';
UPDATE order_items SET unit_price=199.99 WHERE id='b0000000-0000-4000-8000-000000000004';

INSERT INTO order_status_history (id,order_id,old_status,new_status,changed_by_user_id,changed_by_type,changed_at) VALUES
('c0000000-0000-4000-8000-000000000001','a0000000-0000-4000-8000-000000000001',NULL,'processing',NULL,'system','2026-10-01 10:00:00+03'),
('c0000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000002',NULL,'processing',NULL,'system','2026-10-01 12:00:00+03'),
('c0000000-0000-4000-8000-000000000003','a0000000-0000-4000-8000-000000000002','processing','shipped','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','2026-10-02 09:00:00+03'),
('c0000000-0000-4000-8000-000000000004','a0000000-0000-4000-8000-000000000003',NULL,'processing',NULL,'system','2026-10-02 14:00:00+03'),
('c0000000-0000-4000-8000-000000000005','a0000000-0000-4000-8000-000000000003','processing','shipped','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','2026-10-03 08:00:00+03'),
('c0000000-0000-4000-8000-000000000006','a0000000-0000-4000-8000-000000000003','shipped','in_transit',NULL,'system','2026-10-03 11:00:00+03'),
('c0000000-0000-4000-8000-000000000007','a0000000-0000-4000-8000-000000000004',NULL,'processing',NULL,'system','2026-09-28 09:00:00+03'),
('c0000000-0000-4000-8000-000000000008','a0000000-0000-4000-8000-000000000004','processing','shipped','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','2026-09-29 10:00:00+03'),
('c0000000-0000-4000-8000-000000000009','a0000000-0000-4000-8000-000000000004','shipped','in_transit',NULL,'system','2026-09-30 12:00:00+03'),
('c0000000-0000-4000-8000-000000000010','a0000000-0000-4000-8000-000000000004','in_transit','delivered',NULL,'system','2026-10-02 16:00:00+03'),
('c0000000-0000-4000-8000-000000000011','a0000000-0000-4000-8000-000000000005',NULL,'processing',NULL,'system','2026-09-29 10:00:00+03'),
('c0000000-0000-4000-8000-000000000012','a0000000-0000-4000-8000-000000000005','processing','shipped','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','2026-09-30 09:00:00+03'),
('c0000000-0000-4000-8000-000000000013','a0000000-0000-4000-8000-000000000005','shipped','in_transit',NULL,'system','2026-10-01 11:00:00+03'),
('c0000000-0000-4000-8000-000000000014','a0000000-0000-4000-8000-000000000005','in_transit','delivered',NULL,'system','2026-10-03 15:00:00+03');

INSERT INTO payments (id,order_id,provider,transaction_reference,method,status,amount) VALUES
('d0000000-0000-4000-8000-000000000001','a0000000-0000-4000-8000-000000000001','NovaPay','NP-10001','card','paid',899.99),
('d0000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000002','NovaPay','NP-10002','card','paid',1379.98),
('d0000000-0000-4000-8000-000000000003','a0000000-0000-4000-8000-000000000003','NovaPay','NP-10003','wallet','paid',599.98),
('d0000000-0000-4000-8000-000000000004','a0000000-0000-4000-8000-000000000004','NovaPay','NP-10004','card','paid',1299.99),
('d0000000-0000-4000-8000-000000000005','a0000000-0000-4000-8000-000000000005','NovaPay','NP-10005','card','paid',449.99);

INSERT INTO shipments (id,order_id,carrier,tracking_number,status,estimated_delivery,shipped_at,delivered_at) VALUES
('e0000000-0000-4000-8000-000000000001','a0000000-0000-4000-8000-000000000001','NovaShip',NULL,'pending','2026-10-07',NULL,NULL),
('e0000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000002','NovaShip','NOVA-TRK-10002','shipped','2026-10-06','2026-10-02 09:00:00+03',NULL),
('e0000000-0000-4000-8000-000000000003','a0000000-0000-4000-8000-000000000003','NovaShip','NOVA-TRK-10003','in_transit','2026-10-07','2026-10-03 08:00:00+03',NULL),
('e0000000-0000-4000-8000-000000000004','a0000000-0000-4000-8000-000000000004','NovaShip','NOVA-TRK-10004','delivered','2026-10-02','2026-09-29 10:00:00+03','2026-10-02 16:00:00+03'),
('e0000000-0000-4000-8000-000000000005','a0000000-0000-4000-8000-000000000005','NovaShip','NOVA-TRK-10005','delivered','2026-10-03','2026-09-30 09:00:00+03','2026-10-03 15:00:00+03');

INSERT INTO conversations (id,customer_id,status) VALUES
('f0000000-0000-4000-8000-000000000001','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','resolved'),
('f0000000-0000-4000-8000-000000000002','407eeb7b-7942-410f-a28e-68287fe0fb14','open'),
('f0000000-0000-4000-8000-000000000003','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','closed');

INSERT INTO messages (id,conversation_id,sender_type,sender_user_id,content) VALUES
('10000000-0000-4000-8000-000000000001','f0000000-0000-4000-8000-000000000001','customer','76a1912f-8a91-44db-b95c-ff488929d62a','Can you tell me where my order NS-10003 is?'),
('10000000-0000-4000-8000-000000000002','f0000000-0000-4000-8000-000000000001','ai',NULL,'I found order NS-10003. It is currently in transit.'),
('10000000-0000-4000-8000-000000000003','f0000000-0000-4000-8000-000000000001','support_agent','aab4d793-8c91-40d1-b183-c2c4a207abbc','The latest shipment scan shows the package is on its way.'),
('10000000-0000-4000-8000-000000000004','f0000000-0000-4000-8000-000000000002','customer','0e94f508-62ed-4beb-a856-d96f324a4994','I would like to request a refund for my delivered laptop.'),
('10000000-0000-4000-8000-000000000005','f0000000-0000-4000-8000-000000000002','ai',NULL,'A refund above 500 dollars requires human approval.'),
('10000000-0000-4000-8000-000000000006','f0000000-0000-4000-8000-000000000002','support_agent','aab4d793-8c91-40d1-b183-c2c4a207abbc','Your refund request has been submitted for review.'),
('10000000-0000-4000-8000-000000000007','f0000000-0000-4000-8000-000000000003','customer','76a1912f-8a91-44db-b95c-ff488929d62a','Is the NovaView 27 monitor suitable for 4K productivity work?'),
('10000000-0000-4000-8000-000000000008','f0000000-0000-4000-8000-000000000003','ai',NULL,'Yes. The NovaView 27 4K is designed for productivity and content creation.');

INSERT INTO tickets (id,ticket_number,customer_id,conversation_id,assigned_agent_id,category,priority,status,subject,description,resolved_at) VALUES
('20000000-0000-4000-8000-000000000001','TKT-2026-00124','407eeb7b-7942-410f-a28e-68287fe0fb14','f0000000-0000-4000-8000-000000000002','aab4d793-8c91-40d1-b183-c2c4a207abbc','refund','high','waiting_customer','Refund request for NS-10004','Customer requested a full refund for delivered order NS-10004.',NULL),
('20000000-0000-4000-8000-000000000002','TKT-2026-00125','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','f0000000-0000-4000-8000-000000000001','aab4d793-8c91-40d1-b183-c2c4a207abbc','shipping','medium','resolved','Shipping status inquiry','Customer requested an update for order NS-10003.','2026-10-03 12:00:00+03'),
('20000000-0000-4000-8000-000000000003','TKT-2026-00126','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','f0000000-0000-4000-8000-000000000003',NULL,'technical','low','closed','Monitor product question','Customer asked about the NovaView 27 4K for productivity.','2026-10-04 10:00:00+03');

INSERT INTO refunds (id,order_id,customer_id,ticket_id,amount,reason,status,requested_by,approved_by,requested_at,decided_at,completed_at) VALUES
('30000000-0000-4000-8000-000000000001','a0000000-0000-4000-8000-000000000004','407eeb7b-7942-410f-a28e-68287fe0fb14','20000000-0000-4000-8000-000000000001',1299.99,'Full refund for delivered laptop.','pending_approval','0e94f508-62ed-4beb-a856-d96f324a4994',NULL,'2026-10-04 09:00:00+03',NULL,NULL),
('30000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000005','407eeb7b-7942-410f-a28e-68287fe0fb14',NULL,449.99,'Eligible refund for delivered monitor.','completed','0e94f508-62ed-4beb-a856-d96f324a4994','aab4d793-8c91-40d1-b183-c2c4a207abbc','2026-10-04 11:00:00+03','2026-10-04 12:00:00+03','2026-10-05 10:00:00+03');

INSERT INTO documents (id,title,file_name,document_type,source,uploaded_by) VALUES
('40000000-0000-4000-8000-000000000001','NovaStore Refund Policy','refund-policy.pdf','policy','internal://policies/refund-policy.pdf','33a0e628-d157-41d2-b089-b50c87fbb454'),
('40000000-0000-4000-8000-000000000002','NovaStore Shipping Policy','shipping-policy.pdf','policy','internal://policies/shipping-policy.pdf','33a0e628-d157-41d2-b089-b50c87fbb454');

INSERT INTO document_chunks (id,document_id,chunk_index,content,embedding,metadata) VALUES
('50000000-0000-4000-8000-000000000001','40000000-0000-4000-8000-000000000001',0,'Refunds may be requested for eligible delivered products within the applicable refund period.','[0.10,0.20,0.30]','{"topic":"refunds","section":"eligibility"}'),
('50000000-0000-4000-8000-000000000002','40000000-0000-4000-8000-000000000001',1,'Refund requests above 500 dollars require human approval before processing.','[0.20,0.10,0.40]','{"topic":"refunds","section":"approval"}'),
('50000000-0000-4000-8000-000000000003','40000000-0000-4000-8000-000000000002',0,'Customers can track shipped orders using the tracking number provided by the shipping carrier.','[0.30,0.20,0.10]','{"topic":"shipping","section":"tracking"}'),
('50000000-0000-4000-8000-000000000004','40000000-0000-4000-8000-000000000002',1,'Estimated delivery dates are informational and may change during transit.','[0.40,0.10,0.20]','{"topic":"shipping","section":"delivery"}');

INSERT INTO agent_runs (id,conversation_id,customer_id,status,model,started_at,completed_at,error_message,input_tokens,output_tokens,estimated_cost) VALUES
('60000000-0000-4000-8000-000000000001','f0000000-0000-4000-8000-000000000001','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','completed','seed-agent-model','2026-10-03 11:05:00+03','2026-10-03 11:05:04+03',NULL,420,110,0.012500),
('60000000-0000-4000-8000-000000000002','f0000000-0000-4000-8000-000000000002','407eeb7b-7942-410f-a28e-68287fe0fb14','waiting_approval','seed-agent-model','2026-10-04 09:01:00+03',NULL,NULL,520,145,0.016200),
('60000000-0000-4000-8000-000000000003','f0000000-0000-4000-8000-000000000003','9581cd4f-0f8e-4e04-966f-5d45440c6ef3','failed','seed-agent-model','2026-10-04 09:55:00+03','2026-10-04 09:55:02+03','Simulated seed failure for observability testing.',300,40,0.008000);

INSERT INTO tool_calls (id,agent_run_id,tool_name,arguments,result,status,error_message,latency_ms) VALUES
('70000000-0000-4000-8000-000000000001','60000000-0000-4000-8000-000000000001','get_order_status','{"order_number":"NS-10003"}','{"status":"in_transit","tracking_number":"NOVA-TRK-10003"}','success',NULL,120),
('70000000-0000-4000-8000-000000000002','60000000-0000-4000-8000-000000000002','create_refund_request','{"order_number":"NS-10004","amount":1299.99}','{"refund_status":"pending_approval","approval_required":true}','success',NULL,180),
('70000000-0000-4000-8000-000000000003','60000000-0000-4000-8000-000000000003','search_knowledge_base','{"query":"NovaView 27 4K productivity"}',NULL,'failed','Simulated seed tool failure.',950);

INSERT INTO approvals (id,agent_run_id,tool_call_id,ticket_id,action,status,requested_at,decided_at,decided_by,reason) VALUES
('80000000-0000-4000-8000-000000000001','60000000-0000-4000-8000-000000000002','70000000-0000-4000-8000-000000000002','20000000-0000-4000-8000-000000000001','issue_refund','pending','2026-10-04 09:01:05+03',NULL,NULL,'Refund exceeds the human approval threshold.'),
('80000000-0000-4000-8000-000000000002','60000000-0000-4000-8000-000000000001','70000000-0000-4000-8000-000000000001','20000000-0000-4000-8000-000000000002','send_shipping_update','approved','2026-10-03 11:05:02+03','2026-10-03 11:05:03+03','aab4d793-8c91-40d1-b183-c2c4a207abbc','Low-risk customer support action.');

INSERT INTO audit_logs (id,actor_user_id,actor_type,action,entity_type,entity_id,metadata) VALUES
('91000000-0000-4000-8000-000000000001',NULL,'system','order_created','order','a0000000-0000-4000-8000-000000000001','{"order_number":"NS-10001"}'),
('91000000-0000-4000-8000-000000000002','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','order_shipped','order','a0000000-0000-4000-8000-000000000002','{"order_number":"NS-10002"}'),
('91000000-0000-4000-8000-000000000003','76a1912f-8a91-44db-b95c-ff488929d62a','customer','ticket_created','ticket','20000000-0000-4000-8000-000000000002','{"ticket_number":"TKT-2026-00125"}'),
('91000000-0000-4000-8000-000000000004',NULL,'ai','agent_run_completed','agent_run','60000000-0000-4000-8000-000000000001','{"model":"seed-agent-model"}'),
('91000000-0000-4000-8000-000000000005','0e94f508-62ed-4beb-a856-d96f324a4994','customer','refund_requested','refund','30000000-0000-4000-8000-000000000001','{"amount":1299.99}'),
('91000000-0000-4000-8000-000000000006',NULL,'ai','approval_requested','approval','80000000-0000-4000-8000-000000000001','{"reason":"refund_over_threshold"}'),
('91000000-0000-4000-8000-000000000007','aab4d793-8c91-40d1-b183-c2c4a207abbc','support_agent','approval_decided','approval','80000000-0000-4000-8000-000000000002','{"decision":"approved"}'),
('91000000-0000-4000-8000-000000000008','33a0e628-d157-41d2-b089-b50c87fbb454','admin','document_uploaded','document','40000000-0000-4000-8000-000000000001','{"file_name":"refund-policy.pdf"}');

COMMIT;
