namespace sap.esh;
aspect Identifier : {
    key id   : UUID;
    source   : many {
        name : String(4000);
        type : String(4000);
        sid  : String(4000);
    }
}