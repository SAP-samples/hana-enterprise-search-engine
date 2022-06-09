namespace example;

type Name: String(256);

type Number {
    prefix: String(80);
    suffix: String(80);
}

type PhoneNumber: {
    country: String(80);
    number: many Number;
}

type Address: {
    country: String(80);
    zip: String(10);
    city: String(80);
    street: String(80);
    streetNumber: String(80);
    phone: many PhoneNumber;
}

entity Person {
    firstName: Name;
    lastName: Name;
    address: many Address;
}