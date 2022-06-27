namespace example;

type Name : String(256);

entity Person {
    firstName        : Name;
    lastName         : Name;
    address          : {
        country      : String(80);
        zip          : String(10);
        city         : String(80);
        street       : String(80);
        streetNumber : String(80);
    };
}
