CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE upsert_many_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    invalid_data TEXT := '';
BEGIN
    FOR i IN 1..array_length(p_names,1) LOOP
        IF p_phones[i] !~ '^[0-9]+$' THEN
            invalid_data := invalid_data || p_names[i] || ':' || p_phones[i] || ', ';
        ELSE
            CALL upsert_contact(p_names[i], p_phones[i]);
        END IF;
    END LOOP;

    IF invalid_data <> '' THEN
        RAISE NOTICE 'Invalid entries: %', invalid_data;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_name OR phone = p_phone;
END;
$$;