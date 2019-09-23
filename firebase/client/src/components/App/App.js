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
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';

const mapStateToProps = (state) => {
  return { 
    isFetchingRideDate: state.data.isFetchingCurrentRideData,
    rideDate: state.data.currentRideData
  };
};

function RideQuery(props) {
  return (
  <Grid container className="main-grid" spacing={0} justify="center">
    <Grid item className="main-grid-item-ride-selector" xs={12}>
      <RiderSelector />
    </Grid>
    <Grid item className="main-grid-item-ride-viewer" xs={12} align="center">
      <RideViewer isLoading={props.isFetchingRideDate} routeData={props.rideDate} />
    </Grid>
  </Grid>
  )
}

function About() {
  return <h2>This is About</h2>
}
function Users() {
  return <h2>This is Users</h2>
}
function App(props) {
  return (
    
    <>
       <CssBaseline />
       <div className="app">
        <Router>
         <AppBar position="static">
          <Toolbar>
              <Typography variant="h5">OpenBus</Typography>
              <div>
                <nav>
                  <ul>
                    <li>
                      <Link to="/">Ride Query</Link>
                    </li>
                    <li>
                      <Link to="/about/">About</Link>
                    </li>
                    <li>
                      <Link to="/users/">Users</Link>
                    </li>
                  </ul>
                </nav>
              </div>
           </Toolbar>
         </AppBar>
          <Route path="/" exact component={RideQuery} />
          <Route path="/about/" component={About} />
          <Route path="/users/" component={Users} />
        </Router>        
         {/* <Grid container className="main-grid" spacing={0} justify="center">
           <Grid item className="main-grid-item-ride-selector" xs={12}>
             <RiderSelector />
           </Grid>
           <Grid item className="main-grid-item-ride-viewer" xs={12} align="center">
             <RideViewer isLoading={props.isFetchingRideDate} routeData={props.rideDate} />
           </Grid>
         </Grid> */}
       </div>
     </>
  );
}

export default connect(mapStateToProps)(App);