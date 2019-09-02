// TMP FIX for data timezone bug
import addHours from "date-fns/addHours";
import subHours from "date-fns/subHours";
const JERUSALEM_TIMEZONE_OFFSET = 3;

export function fetchAgenciesAndRides(date) {
    const firestore = window.firebase.firestore();

    return firestore.collection("agency_days").where("date", "==", dateForQuery(date))
        .get()
        .then(extractDocs);
} 

export function fetchRouteRides(date, agencyId, lineShortName) {
    const firestore = window.firebase.firestore();

    const query = firestore.collection("route_days")
        .where("date", "==", dateForQuery(date))
        .where("agency_id", "==", agencyId)
        .where("route_short_name", "==", lineShortName);
    return query.get().then(extractDocs);
}

export function fetchRideData(routeId, dateTime) {
    const firestore = window.firebase.firestore();

    // TMP FIX: addHours for the data timezone bug
    const queryDateTime = addHours(dateTime, JERUSALEM_TIMEZONE_OFFSET);

    const query = firestore.collection("siri_rides")
        .where("route_id", "==", routeId)
        .where("planned_start_datetime", "==", queryDateTime);
    return query.get()
        .then(extractDocs)
        .then(convertRideDataPointsDates);
}

function convertRideDataPointsDates(docs) {
    /* TMP FIX: addHours/subHours for the data timezone bug
     * (When fixed, just do timestamp.toDate() to convert firebase's Timestamp
     * to js Date) */
    const fixDate = (timestamp) => subHours(timestamp.toDate(), JERUSALEM_TIMEZONE_OFFSET);
    
    for (const doc of docs) {
        for (const point of doc.points) {
            point.pred_dt = fixDate(point.pred_dt);
            point.rec_dt = fixDate(point.rec_dt);
        }
    }

    return docs;
}

function dateForQuery(date) {
    // Make sure the date doesn't have a "time part" (=midnight UTC)
    const queryDate = new Date(date.getTime());
    queryDate.setUTCHours(0, 0, 0, 0);

    return queryDate;
}

const extractDocs = (querySnapshot) => querySnapshot.docs.map((doc) => doc.data());