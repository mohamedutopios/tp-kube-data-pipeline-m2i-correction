db = db.getSiblingDB('compliance');
db.agents.drop();
db.agents.insertMany([
  { first: "Alice", last: "Durand" },
  { first: "Karim", last: "Benali" },
  { first: "Nora",  last: "Bensaid" },
  { first: "Yves",  last: "Leroux" },
  { first: "Lila",  last: "Ferri" }
]);
