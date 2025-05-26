-- VÅRE CHANGES --
USE varehusdb;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowInventory`()
BEGIN
    SELECT * FROM varehusdb.vare;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowOrders`()
BEGIN
    SELECT * FROM varehusdb.ordre;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowContactsAmount`()
BEGIN
    SELECT COUNT(KNr) FROM varehusdb.kunde;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `ShowContacts`()
BEGIN
    SELECT * FROM varehusdb.kunde;
END$$

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

CREATE DEFINER=`root`@`localhost` PROCEDURE `RemoveContacts`(IN p_KNr INT)
BEGIN
    -- Declare variables at the very start
    DECLARE order_count INT DEFAULT 0;
    DECLARE orderline_count INT DEFAULT 0;

    -- Start a transaction to ensure data integrity
    START TRANSACTION;

    -- First, count and delete all order lines associated with this customer's orders
    SELECT COUNT(*) INTO orderline_count
    FROM `varehusdb`.`ordrelinje` ol
             INNER JOIN `varehusdb`.`ordre` o ON ol.OrdreNr = o.OrdreNr
    WHERE o.KNr = p_KNr;

    -- Delete the order lines
    DELETE ol FROM `varehusdb`.`ordrelinje` ol
                       INNER JOIN `varehusdb`.`ordre` o ON ol.OrdreNr = o.OrdreNr
    WHERE o.KNr = p_KNr;

    -- Count and delete all orders from this customer
    SELECT COUNT(*) INTO order_count
    FROM `varehusdb`.`ordre`
    WHERE KNr = p_KNr;

    -- Delete the orders
    DELETE FROM `varehusdb`.`ordre`
    WHERE KNr = p_KNr;

    -- Finally, delete the customer record
    DELETE FROM `varehusdb`.`kunde`
    WHERE KNr = p_KNr;

    -- Commit the transaction if all deletions were successful
    COMMIT;

    -- Return confirmation with counts of deleted items
    SELECT
        p_KNr AS CustomerID,
        'Deleted successfully' AS Status,
        order_count AS OrdersRemoved,
        orderline_count AS OrderLinesRemoved;
END$$
DELIMITER ;