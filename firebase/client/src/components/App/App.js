import "./App.css";

import React from "react";
// import RideViewer from "../RideViewer";
// import RiderSelector from "../RideSelector";
// import { connect } from "react-redux";
// import Grid from "@material-ui/core/Grid";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import CssBaseline from '@material-ui/core/CssBaseline';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import RideQuery from './../RideQuery/RideQuery';

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
       </div>
     </>
  );
}

export default App;