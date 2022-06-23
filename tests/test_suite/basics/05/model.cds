namespace example;

type Name: String(256);

type PhoneNumber: {
    country: String(80);
    provider: String(80);
    number: String(80);
}

type Address: {
    country: String(80);
    zip: String(10);
    city: String(80);
    street: String(80);
    streetNumber: String(80);
    phone: PhoneNumber;
}

entity Person {
    firstName: Name;
    lastName: Name;
    address: many Address;
}