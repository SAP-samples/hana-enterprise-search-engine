namespace example;

entity Person {
    firstName          : String(256);
    lastName           : String(256);
    address            : {
        country        : String(80);
        zip            : String(10);
        city           : String(80);
        street         : String(80);
        streetNumber   : String(80);
        phone          : {
            country    : String(80);
            number     : {
                prefix : String(80);
                suffix : String(80);
            };
        };
    };
}
