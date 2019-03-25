const fs = require('fs');
const path = require('path');
const express = require('express');
const morgan = require('morgan');

const trips = require('./trips.json');

const app = express();

const accessLogStream = fs.createWriteStream(path.join(__dirname, 'access.log'), { flags: 'a' });
app.use(morgan('combined', { stream: accessLogStream }));

app.get('/trips/:id', (req, res) => {
   const tripId = req.params.id;
   const trip = trips[tripId];

   if (trip) {
      res.json(trip);
   } else {
      res.status(404).end(`No trip with id ${tripId}`);
   }
});

app.listen(3000, () => {
   console.log('Listening on port 3000');
});
