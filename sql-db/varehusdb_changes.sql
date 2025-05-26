-- Endringer for å få programmet fungerende. Alle stored procedures og endringer i databasen: --

USE varehusdb;

-- Legger til auto-increment på KNr i kunde-tabellen --
START TRANSACTION;
    ALTER TABLE `varehusdb`.`ordre` 
    DROP FOREIGN KEY `OrdreKundeFN`;

    ALTER TABLE `varehusdb`.`kunde` 
    MODIFY COLUMN `KNr` INT NOT NULL AUTO_INCREMENT;

    ALTER TABLE `varehusdb`.`ordre`
    ADD CONSTRAINT `OrdreKundeFN`
    FOREIGN KEY (`KNr`) 
    REFERENCES `varehusdb`.`kunde` (`KNr`);

COMMIT;

DELIMITER $$
-- Prosedyre for å vise lager --
CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowInventory`()
BEGIN
    SELECT * FROM varehusdb.vare;
END$$

-- Prosedyre for å vise ordrer --
CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowOrders`()
BEGIN
    SELECT * FROM varehusdb.ordre;
END$$

-- Prosedyre for å vise antall kunder --
CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowContactsAmount`()
BEGIN
    SELECT COUNT(KNr) FROM varehusdb.kunde;
END$$

-- Prosedyre for å vise kunder --
CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowContacts`()
BEGIN
    SELECT * FROM varehusdb.kunde;
END$$

-- Prosedyre for å vise ordre-innhold --
CREATE PROCEDURE ShowOrderContents(IN order_id INT)
BEGIN
    SELECT
        v.Betegnelse AS VareNavn,
        ol.VNr,
        ol.Antall,
        ol.PrisPrEnhet,
        k.Fornavn,
        k.Etternavn,
        k.Adresse,
        k.PostNr
    FROM varehusdb.ordrelinje AS ol
             JOIN vare v ON ol.VNr = v.VNr
             JOIN ordre o ON ol.OrdreNr = o.OrdreNr
             JOIN kunde k ON o.KNr = k.KNr
    WHERE ol.OrdreNr = order_id;
END$$

-- Prosedyre for å lage en ny kunde --
CREATE DEFINER=`root`@`localhost` PROCEDURE `AddContacts`(
    IN p_Fornavn VARCHAR(50),
    IN p_Etternavn VARCHAR(50),
    IN p_Adresse VARCHAR(100),
    IN p_PostNr CHAR(4)
)
BEGIN
    INSERT INTO kunde (Fornavn, Etternavn, Adresse, PostNr)
    VALUES (p_Fornavn, p_Etternavn, p_Adresse, p_PostNr);
END$$

-- Prosedyre for å editere kunde --
CREATE DEFINER=`root`@`localhost` PROCEDURE `EditContacts`(
    IN p_KNr INT,
    IN p_Fornavn VARCHAR(50),
    IN p_Etternavn VARCHAR(50),
    IN p_Adresse VARCHAR(100),
    IN p_PostNr CHAR(4)
)
BEGIN
    UPDATE kunde
    SET Fornavn = p_Fornavn,
        Etternavn = p_Etternavn,
        Adresse = p_Adresse,
        PostNr = p_PostNr
    WHERE KNr = p_KNr;
END$$

-- Prosedyre for å fjerne kunde --
CREATE DEFINER=`root`@`localhost` PROCEDURE `RemoveContacts`(IN p_KNr INT)
BEGIN
    -- Setter variabler helt i starten
    DECLARE order_count INT DEFAULT 0;
    DECLARE orderline_count INT DEFAULT 0;

    START TRANSACTION;
    -- Teller og sletter alle ordrelinjer knyttet til kundens ordre
    SELECT COUNT(*) INTO orderline_count
    FROM `varehusdb`.`ordrelinje` ol
             INNER JOIN `varehusdb`.`ordre` o ON ol.OrdreNr = o.OrdreNr
    WHERE o.KNr = p_KNr;

    -- Sletter ordrelinjer
    DELETE ol FROM `varehusdb`.`ordrelinje` ol
                       INNER JOIN `varehusdb`.`ordre` o ON ol.OrdreNr = o.OrdreNr
    WHERE o.KNr = p_KNr;

    -- Teller og slett alle ordre fra kunden
    SELECT COUNT(*) INTO order_count
    FROM `varehusdb`.`ordre`
    WHERE KNr = p_KNr;

    -- Sletter ordrene
    DELETE FROM `varehusdb`.`ordre`
    WHERE KNr = p_KNr;

    -- Sletter til slutt kunde
    DELETE FROM `varehusdb`.`kunde`
    WHERE KNr = p_KNr;

    COMMIT;

    -- Returner bekreftelse med antall slettede elementer
    SELECT
        p_KNr AS CustomerID,
        'Deleted successfully' AS Status,
        order_count AS OrdersRemoved,
        orderline_count AS OrderLinesRemoved;
END$$
DELIMITER ;