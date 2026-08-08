from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Produtor(Base):
    __tablename__ = "produtores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    senha_hash = Column(String(200), nullable=False)
    municipio = Column(String(100))
    estado = Column(String(2), default="AL")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    colmeias = relationship("Colmeia", back_populates="produtor")
    lotes = relationship("Lote", back_populates="produtor")


class Colmeia(Base):
    __tablename__ = "colmeias"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)  # C-01, C-02...
    produtor_id = Column(Integer, ForeignKey("produtores.id"), nullable=False)
    florada = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(20), default="normal")  # normal, alerta, critico
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())

    produtor = relationship("Produtor", back_populates="colmeias")
    leituras = relationship("LeituraSensor", back_populates="colmeia")
    lotes_colmeias = relationship("LoteColmeia", back_populates="colmeia")


class LeituraSensor(Base):
    __tablename__ = "leituras_sensor"

    id = Column(Integer, primary_key=True, index=True)
    colmeia_id = Column(Integer, ForeignKey("colmeias.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    temperatura = Column(Float)   # °C
    umidade = Column(Float)       # %
    peso = Column(Float)          # kg
    som = Column(Float)           # Hz
    status_calculado = Column(String(20), default="normal")

    colmeia = relationship("Colmeia", back_populates="leituras")


class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, index=True, nullable=False)  # LT-2026-001
    produtor_id = Column(Integer, ForeignKey("produtores.id"), nullable=False)
    florada = Column(String(300))
    data_extracao = Column(DateTime(timezone=True))
    volume_kg = Column(Float)
    status_lab = Column(String(30), default="em_analise")  # aprovado, reprovado, em_analise
    qr_code_url = Column(String(500))
    destino = Column(String(300))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    produtor = relationship("Produtor", back_populates="lotes")
    colmeias_lote = relationship("LoteColmeia", back_populates="lote")
    etapas = relationship("EtapaCadeia", back_populates="lote", order_by="EtapaCadeia.ordem")
    laudo = relationship("Laudo", back_populates="lote", uselist=False)


class LoteColmeia(Base):
    """Relação N:N entre Lote e Colmeia"""
    __tablename__ = "lotes_colmeias"

    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    colmeia_id = Column(Integer, ForeignKey("colmeias.id"), nullable=False)

    lote = relationship("Lote", back_populates="colmeias_lote")
    colmeia = relationship("Colmeia", back_populates="lotes_colmeias")


class EtapaCadeia(Base):
    """Etapas da cadeia produtiva — rastreabilidade"""
    __tablename__ = "etapas_cadeia"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    ordem = Column(Integer, nullable=False)
    tipo = Column(String(50))  # colmeia, monitoramento, extracao, analise, envase, distribuicao, venda
    titulo = Column(String(200))
    data = Column(String(100))
    local = Column(String(200))
    detalhe = Column(Text)
    icone = Column(String(10))
    concluida = Column(Boolean, default=True)

    lote = relationship("Lote", back_populates="etapas")


class Laudo(Base):
    __tablename__ = "laudos"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), unique=True, nullable=False)
    data_analise = Column(DateTime(timezone=True))
    laboratorio = Column(String(200))
    responsavel_tecnico = Column(String(200))
    brix = Column(Float)
    ph = Column(Float)
    hmf = Column(Float)        # mg/kg
    diastase = Column(Float)   # DN
    umidade_mel = Column(Float) # %
    cor = Column(String(50))
    aprovado = Column(Boolean, default=True)
    observacoes = Column(Text)

    lote = relationship("Lote", back_populates="laudo")
