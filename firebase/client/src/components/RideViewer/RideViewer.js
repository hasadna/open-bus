import "./RideViewer.css";
import AutoFocusFeatureGroup from "./AutoFocusFeatureGroup";

import React from "react";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import CircularProgress from '@material-ui/core/CircularProgress';
import { Map, TileLayer, Marker, Popup, Tooltip } from "react-leaflet";
import lightFormat from "date-fns/lightFormat";

function renderNoData(isLoading) {
    if (isLoading) {
        // Note: The "div" around CircularProgress is currently there to center it horizontally
        return (
            <div>
                <CircularProgress />
            </div>
        );  
    }

    return (
        <Typography variant="h3" color="textSecondary">
            Please select a ride
        </Typography>
    )
}

function renderPoint(point) {
    const {latitude, longitude} = point.point;
    return (
        <Marker position={[latitude, longitude]}>
          <Popup>
              {latitude}, {longitude}
              <br/>
              Predicted: {lightFormat(point.predictedDateTime, "HH:mm:ss")} 
          </Popup>
          <Tooltip permanent>
            {lightFormat(point.recordedDateTime, "HH:mm:ss")}
          </Tooltip>
        </Marker>
    );
}

function renderMap(data) {
    return (
        <Map className="map">
            <TileLayer
                attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <AutoFocusFeatureGroup>
                {data.points.map(renderPoint)}
            </AutoFocusFeatureGroup>
        </Map>
    );
}

function RideViewer(props) {
    return (
        <Paper className="route-viewer">
            { props.routeData ? renderMap(props.routeData) : renderNoData(props.isLoading) }
        </Paper>
    );
}

export default React.memo(RideViewer);