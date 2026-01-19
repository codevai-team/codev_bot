-- Миграция для добавления поля project_url в таблицу projects
-- Запустите этот скрипт в вашей базе данных PostgreSQL

-- Добавляем новое поле project_url
ALTER TABLE projects 
ADD COLUMN IF NOT EXISTS project_url TEXT;

-- Проверяем результат
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'projects' 
ORDER BY ordinal_position;

-- Сообщение об успешном выполнении
DO $$ 
BEGIN 
    RAISE NOTICE 'Миграция выполнена успешно! Поле project_url добавлено в таблицу projects.';
END $$;
