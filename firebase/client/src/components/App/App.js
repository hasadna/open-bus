import "./App.css";
import RiderSelector from "../RideSelector";
import RideViewer from "../RideViewer";

import React from "react";
import { connect } from "react-redux";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import CssBaseline from '@material-ui/core/CssBaseline';

const mapStateToProps = (state) => {
  return { 
    isFetchingRideDate: state.data.isFetchingCurrentRideData,
    rideDate: state.data.currentRideData
  };
};

function App(props) {
  return (
    <>
      <CssBaseline />
      <div className="app">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h5">OpenBus</Typography>
          </Toolbar>
        </AppBar>
        <Grid container className="main-grid" spacing={0} justify="center">
          <Grid item className="main-grid-item-ride-selector" xs={12}>
            <RiderSelector />
          </Grid>
          <Grid item className="main-grid-item-ride-viewer" xs={12} align="center">
            <RideViewer isLoading={props.isFetchingRideDate} routeData={props.rideDate} />
          </Grid>
        </Grid>
      </div>
    </>
  );
}

export default connect(mapStateToProps)(App);