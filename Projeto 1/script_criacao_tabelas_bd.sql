create database chat_ia_db;
use chat_ia_db;

-- Tabela de usuario
create table usuario(
	idusuario int auto_increment primary key,
    nome varchar(100) not null,
    email varchar(50) unique not null, 
    senha varchar(50) not null
);

-- Tabela de chat
create table chat (
	idchat int auto_increment primary key,
    titulo varchar(100) not null, 
    data_criacao datetime default current_timestamp,
    idusuario int,
    foreign key(idusuario) references usuario(idusuario) on delete cascade
);

-- tabela de mensagens
create table mensagem(
	idmensagem int auto_increment primary key,
    conteudo text not null,
    origem enum('usuario', 'LLM') not null, 
    enviado_em datetime default current_timestamp,
    idusuario int, 
    idchat int, 
    foreign key(idusuario) references usuario(idusuario) on delete cascade,
    foreign key(idchat) references chat(idchat) on delete cascade
);

-- Tabela de fazenda
create table fazenda(
	idfazenda int auto_increment primary key,
    nome varchar(100) not null, 
    municipio varchar(100) not null,
    estado varchar(2) not null
);

-- Tabela de animais inseminados
create table animal_inseminado(
	idanimal_inseminado int auto_increment primary key,
    numero_animal varchar(45) not null,
    lote varchar(45) not null, 
    raca varchar(45) not null, 
    categoria varchar(45) not null, 
    ECC decimal(3,2) not null, 
    ciclicidade tinyint(1) not null,
    idfazenda int,
    foreign key(idfazenda) references fazenda(idfazenda) on delete cascade    
);

-- Tabela de informações sobre a inseminação
create table inseminacao(
	idinseminacao int auto_increment primary key,
    protocolo varchar(45), 
    implante_p4 varchar(45),
    empresa  varchar(45),
    gnrh_na_IA tinyint,
    pgf_no_d0 tinyint,
    dose_pgf_retirada varchar(45),
    marca_pgf_retirada varchar(45),
    dose_ce varchar(45), 
    ECG varchar(45),
    dose_ecg varchar(45), 
    touro varchar(45),
    raca_touro varchar(45),
    empresa_touro varchar(45),
    inseminador varchar(45),
    numero_IATF varchar(45),
    DG tinyint,
    vazia_com_ou_sem_CL tinyint,
    perda tinyint,
    idanimal_inseminado int,
    foreign key (idanimal_inseminado) references animal_inseminado(idanimal_inseminado) on delete cascade
);

select * from fazenda;
select * from animal_inseminado where idfazenda = 6;
select * from inseminacao;
select * from usuario;
select * from chat;
select * from mensagem;

select * from animal_inseminado where raca = "Nelore";
SELECT * FROM animal_inseminado;
SELECT * FROM inseminacao where protocolo = "9 dias" and perda = 0;


SELECT
    protocolo,
    COUNT(*) AS total_protocolos,
    SUM(CASE WHEN DG = 0 AND perda = 0 THEN 1 ELSE 0 END) AS sucesso,
    ROUND(
        (SUM(CASE WHEN DG = 0 AND perda = 0 THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) AS taxa_sucesso_percentual
FROM inseminacao
GROUP BY protocolo
ORDER BY taxa_sucesso_percentual DESC;

SELECT Raca, COUNT(*) as Frequencia
FROM animal_inseminado
GROUP BY Raca
ORDER BY Frequencia DESC;

SELECT 
            f.idfazenda, f.nome AS fazenda_nome, f.municipio, f.estado,
            a.idanimal_inseminado, a.numero_animal, a.lote, a.raca AS raca_animal, a.categoria, a.ECC, a.ciclicidade,
            i.idinseminacao, i.protocolo, i.touro, i.raca_touro, i.empresa_touro, i.inseminador, 
            i.numero_IATF, i.DG, i.vazia_com_ou_sem_CL, i.perda
        FROM fazenda f
        JOIN animal_inseminado a ON f.idfazenda = a.idfazenda
        JOIN inseminacao i ON a.idanimal_inseminado = i.idanimal_inseminado;

select * from fazenda;
ALTER TABLE fazenda ADD COLUMN embedding JSON;
INSERT INTO fazenda (nome, municipio, estado) VALUES
('Fazenda Boa Esperança', 'Ribeirão Preto', 'SP'),
('Fazenda Santo Antônio', 'Uberaba', 'MG'),
('Fazenda Verde Vale', 'Campo Grande', 'MS'),
('Fazenda Santa Luzia', 'Goiânia', 'GO'),
('Fazenda São João', 'Dourados', 'MS');


select * from animal_inseminado where idfazenda=4;


























