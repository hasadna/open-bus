import React from "react";
import { connect } from "react-redux";
import RideViewer from "../RideViewer";
import RiderSelector from "../RideSelector";
import Grid from "@material-ui/core/Grid";
import PropTypes from 'prop-types';

const RideQuery = props => {
    const { isFetchingRideDate, rideDate } = props
  return (
    <Grid container className="main-grid" spacing={0} justify="center">
      <Grid item className="main-grid-item-ride-selector" xs={12}>
        <RiderSelector />
      </Grid>
      <Grid item className="main-grid-item-ride-viewer" xs={12} align="center">
        <RideViewer
          isLoading={isFetchingRideDate}
          routeData={rideDate}
        />
      </Grid>
    </Grid>
  );
};

RideQuery.propTypes = {
    isFetchingCurrentRideData:PropTypes.object,
    routeData: PropTypes.object
}

const mapStateToProps = state => {
  return {
    isFetchingRideDate: state.data.isFetchingCurrentRideData,
    rideDate: state.data.currentRideData
  };
};
export default connect(mapStateToProps)(RideQuery);
