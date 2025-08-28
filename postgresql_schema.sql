-- Script de creación de tablas PostgreSQL para WhatsApp API Microservice
-- Optimizado para soporte nativo de UUID

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de líneas de mensajería
CREATE TABLE IF NOT EXISTS messaging_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    whatsapp_business_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    webhook_verify_token VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    max_daily_messages INTEGER DEFAULT 1000,
    current_daily_messages INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de mensajes
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    whatsapp_msg_id VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    contact_name VARCHAR(255),
    message_type VARCHAR(50) NOT NULL,
    content TEXT,
    media_url TEXT,
    media_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    line_id UUID REFERENCES messaging_lines(id),
    webhook_id UUID,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de contactos
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    profile_pic_url TEXT,
    last_seen TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de eventos de webhook
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_attempts INTEGER DEFAULT 0,
    last_processing_attempt TIMESTAMP,
    error_message TEXT,
    line_id UUID REFERENCES messaging_lines(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de archivos multimedia
CREATE TABLE IF NOT EXISTS media_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    whatsapp_media_id VARCHAR(255) UNIQUE,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_path TEXT,
    download_url TEXT,
    downloaded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de flujos de conversación (RiveScript)
CREATE TABLE IF NOT EXISTS conversation_flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rivescript_content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 1,
    fallback_to_llm BOOLEAN DEFAULT TRUE,
    max_context_messages INTEGER DEFAULT 5,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de contextos de conversación
CREATE TABLE IF NOT EXISTS conversation_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    current_topic VARCHAR(100),
    context_data JSONB DEFAULT '{}',
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flow_id UUID REFERENCES conversation_flows(id),
    session_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de interacciones del chatbot
CREATE TABLE IF NOT EXISTS chatbot_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT,
    intent VARCHAR(100),
    confidence_score DECIMAL(3,2),
    flow_id UUID REFERENCES conversation_flows(id),
    context_id UUID REFERENCES conversation_contexts(id),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_messages_phone_created ON messages(phone_number, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_whatsapp_id ON messages(whatsapp_msg_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON webhook_events(processed, created_at);
CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_number);
CREATE INDEX IF NOT EXISTS idx_media_files_whatsapp_id ON media_files(whatsapp_media_id);
CREATE INDEX IF NOT EXISTS idx_conversation_flows_active ON conversation_flows(is_active, priority);
CREATE INDEX IF NOT EXISTS idx_conversation_contexts_phone ON conversation_contexts(phone_number);
CREATE INDEX IF NOT EXISTS idx_chatbot_interactions_phone_created ON chatbot_interactions(phone_number, created_at DESC);

-- Triggers para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a todas las tablas
CREATE TRIGGER update_messaging_lines_updated_at BEFORE UPDATE ON messaging_lines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_webhook_events_updated_at BEFORE UPDATE ON webhook_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_media_files_updated_at BEFORE UPDATE ON media_files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversation_flows_updated_at BEFORE UPDATE ON conversation_flows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversation_contexts_updated_at BEFORE UPDATE ON conversation_contexts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
