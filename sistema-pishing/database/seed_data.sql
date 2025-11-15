INSERT INTO users (email, name, role)
VALUES ('admin@company.com', 'Administrador', 'ADMIN'),
       ('analyst@company.com', 'Analista', 'ANALYST')
ON CONFLICT (email) DO NOTHING;
