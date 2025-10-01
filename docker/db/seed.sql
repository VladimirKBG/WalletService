INSERT INTO wallets (id, balance, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000001'::uuid, 1000.00, now(), now()),

INSERT INTO operations (id, wallet_id, operation_type, amount, created_at)
VALUES
  ('10000000-0000-0000-0000-000000000001'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'DEPOSIT', 1000.00, now());