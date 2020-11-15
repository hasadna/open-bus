// removed by eldad 07/01/2019

//package il.org.hasadna.siri_client.gtfs.main;
//
//import static org.junit.Assert.*;
//
//import java.io.IOException;
//import java.nio.file.Path;
//import java.time.LocalDate;
//import java.util.*;
//import java.util.stream.Collectors;
//
//import il.org.hasadna.siri_client.gtfs.analysis.GtfsDataManipulations;
//import il.org.hasadna.siri_client.gtfs.analysis.SchedulingDataCreator;
//import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
//import il.org.hasadna.siri_client.gtfs.crud.GtfsFtp;
//import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;
//import org.junit.Before;
//import org.junit.Test;
//
//import il.org.hasadna.siri_client.gtfs.analysis.GtfsRecord;
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;
//
//public class DefaultGtfsQueryBasedOnFtpTest {
//
//	private static Logger logger = LoggerFactory.getLogger(DefaultGtfsQueryBasedOnFtpTest.class);
//
//	@Before
//	public void setUp() throws Exception {
//	}
//
//	@Test
//	public void testExec() throws IOException {
//		DefaultGtfsQueryBasedOnFtp defaultGtfsQueryBasedOnFtp = new DefaultGtfsQueryBasedOnFtp(LocalDate.now());
//		Collection<GtfsRecord> res = defaultGtfsQueryBasedOnFtp.exec();
//
//		res.forEach(System.out::println);
//	}
//
//	@Test
//	public void testWithoutDownload() {
//
//		DefaultGtfsQueryBasedOnFtp x = new DefaultGtfsQueryBasedOnFtp();
//		x.configProperties.agencies = new ArrayList<>();
//				//Arrays.asList("3","5","16","18");
//		x.run(false);
//	}
//
//	@Test
//	public void testJsonForSpecificRoute() throws IOException {
//
//		LocalDate date = LocalDate.now();
//
//		Path olderGtfs = GtfsFtp.findOlderGtfsFile(LocalDate.now());
//		Path pathToGtfsFile = olderGtfs;    // default value, if we can't download a new GTFS
//
//
//		GtfsZipFile gtfsZipFile = new GtfsZipFile(pathToGtfsFile);
//		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile);
//
//		GtfsDataManipulations gtfs = new GtfsDataManipulations(gtfsCrud);
//		date = LocalDate.now();
//		Collection<GtfsRecord> records = gtfs.combine(date);
//		logger.info("size: {}", records.size());
//
//		SchedulingDataCreator schedulingDataCreator = new SchedulingDataCreator();
//		Optional<String> json1 = schedulingDataCreator.generateJsonFor("15531", records, gtfs, date);
//		Optional<String> json2 = schedulingDataCreator.generateJsonFor("15532", records, gtfs, date);
//
//	}
//
//	@Test
//	public void testJsonForSeveralRoutes() throws IOException {
//
//		List<String> routes = parseRoutes();
//
//		Path olderGtfs = GtfsFtp.findOlderGtfsFile(LocalDate.now());
//		Path pathToGtfsFile = olderGtfs;    // default value, if we can't download a new GTFS
//
//
//		GtfsZipFile gtfsZipFile = new GtfsZipFile(pathToGtfsFile);
//		GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile);
//
//		GtfsDataManipulations gtfs = new GtfsDataManipulations(gtfsCrud);
//		final LocalDate date = LocalDate.now();
//		Collection<GtfsRecord> records = gtfs.combine(date);
//		logger.info("size: {}", records.size());
//
//		SchedulingDataCreator schedulingDataCreator = new SchedulingDataCreator();
//		Set<String> makats = schedulingDataCreator.findMakats(routes, records, gtfs, date);
//
//		List<String> routeIds = new ArrayList<>();
//		for (String makat : makats) {
//			List<String> routesOfThisMakat =
//				gtfs.getRoutes().values().stream()
//					.filter(route -> makat.equals(route.getRouteDesc().substring(0, 5)))
//					.map(route -> route.getRouteId())
//					.collect(Collectors.toList());
//			routeIds.addAll(routesOfThisMakat);
//		}
//
//		List<String> jsons = new ArrayList<>();
//		for (String route : routeIds) {
//			Optional<String> json = schedulingDataCreator.generateJsonFor(route, records, gtfs, date);
//			if (json.isPresent()) {
//				jsons.add(json.get());
//			}
//		}
//		String json = "{  \"data\" :[" + jsons.stream().collect(Collectors.joining(",")) + "]}";
//		logger.info(json);
//	}
//
//	private String parseLongName(String routeLongName) {
//		String result = "";
//		try {
//			String[] parts = routeLongName.split("<->");
//			if (parts.length == 2) {
//				String from = parts[0];
//				String fromCity = from.split("-")[1];
//
//				String to = parts[1];
//				String toCity = to.split("-")[1];
//
//				if (fromCity.equals(toCity)) {
//					result = "ב" +fromCity ;
//				}
//				else {
//					result = "מ" +fromCity + " אל" + " " + toCity;
//				}
//			}
//		}
//		catch (Exception ex) {
//			// parsing failed, so
//			result = "";
//		}
//		return result;
//	}
//
//
//	private List<String> parseRoutes() {
//		List<String> routes = new ArrayList<>();
//		String[] lines = someRoutes.split("\n");
//		for (String line : lines) {
//			String routeId = line.split(":")[1].split("\"")[1] ;
//			routes.add(routeId);
//		}
//		return routes;
//	}
//
//	private String someRoutes = "  \"lineRef\" : \"3093\",\n" +
//			"  \"lineRef\" : \"19585\",\n" +
//			"  \"lineRef\" : \"3102\",\n" +
//			"  \"lineRef\" : \"20097\",\n" +
//			"  \"lineRef\" : \"3091\",\n" +
//			"  \"lineRef\" : \"3096\",\n" +
//			"  \"lineRef\" : \"3097\",\n" +
//			"  \"lineRef\" : \"3092\",\n" +
//			"  \"lineRef\" : \"15031\",\n" +
//			"  \"lineRef\" : \"10332\",\n" +
//			"  \"lineRef\" : \"22986\",\n" +
//			"  \"lineRef\" : \"10333\",\n" +
//			"  \"lineRef\" : \"19799\",\n" +
//			"  \"lineRef\" : \"19800\",\n" +
//			"    \"lineRef\" : \"7117\",\n" +
//			"    \"lineRef\" : \"19740\",\n" +
//			"    \"lineRef\" : \"7224\",\n" +
//			"    \"lineRef\" : \"15438\",\n" +
//			"    \"lineRef\" : \"15439\",\n" +
//			"    \"lineRef\" : \"7020\",\n" +
//			"    \"lineRef\" : \"7023\",\n" +
//			"    \"lineRef\" : \"3792\",\n" +
//			"    \"lineRef\" : \"3701\",\n" +
//			"    \"lineRef\" : \"13136\",\n" +
//			"    \"lineRef\" : \"16067\",\n" +
//			"    \"lineRef\" : \"3703\",\n" +
//			"    \"lineRef\" : \"7453\",\n" +
//			"    \"lineRef\" : \"19741\",\n" +
//			"    \"lineRef\" : \"15529\",\n" +
//			"    \"lineRef\" : \"17177\",\n" +
//			"      \"lineRef\" : \"6672\",\n" +
//			"      \"lineRef\" : \"8237\",\n" +
//			"      \"lineRef\" : \"8238\",\n" +
//			"      \"lineRef\" : \"8244\",\n" +
//			"      \"lineRef\" : \"8245\",\n" +
//			"      \"lineRef\" : \"19732\",\n" +
//			"      \"lineRef\" : \"10802\",\n" +
//			"      \"lineRef\" : \"10801\",\n" +
//			"      \"lineRef\" : \"15085\",\n" +
//			"      \"lineRef\" : \"11806\",\n" +
//			"      \"lineRef\" : \"10804\",\n" +
//			"      \"lineRef\" : \"10807\",\n" +
//			"      \"lineRef\" : \"10806\",\n" +
//			"      \"lineRef\" : \"15086\",\n" +
//			"      \"lineRef\" : \"12425\",\n" +
//			"      \"lineRef\" : \"12424\",\n" +
//			"      \"lineRef\" : \"17370\",\n" +
//			"      \"lineRef\" : \"17371\",\n" +
//			"      \"lineRef\" : \"10799\",\n" +
//			"      \"lineRef\" : \"10797\",\n" +
//			"      \"lineRef\" : \"17361\",\n" +
//			"      \"lineRef\" : \"10398\",\n" +
//			"      \"lineRef\" : \"17362\",\n" +
//			"      \"lineRef\" : \"10399\",\n" +
//			"      \"lineRef\" : \"10403\",\n" +
//			"      \"lineRef\" : \"10400\",\n" +
//			"      \"lineRef\" : \"10402\",\n" +
//			"      \"lineRef\" : \"10401\",\n" +
//			"      \"lineRef\" : \"12871\",\n" +
//			"      \"lineRef\" : \"10379\",\n" +
//			"      \"lineRef\" : \"10381\",\n" +
//			"      \"lineRef\" : \"10383\",\n" +
//			"      \"lineRef\" : \"10384\",\n" +
//			"      \"lineRef\" : \"10747\",\n" +
//			"      \"lineRef\" : \"10746\",\n" +
//			"      \"lineRef\" : \"12112\",\n" +
//			"      \"lineRef\" : \"13435\",\n" +
//			"      \"lineRef\" : \"10389\",\n" +
//			"      \"lineRef\" : \"10391\",\n" +
//			"      \"lineRef\" : \"10393\",\n" +
//			"      \"lineRef\" : \"22860\",\n" +
//			"      \"lineRef\" : \"22898\",\n" +
//			"      \"lineRef\" : \"9833\",\n" +
//			"      \"lineRef\" : \"12400\",\n" +
//			"      \"lineRef\" : \"12401\",\n" +
//			"      \"lineRef\" : \"9834\",\n" +
//			"      \"lineRef\" : \"12439\",\n" +
//			"      \"lineRef\" : \"9838\",\n" +
//			"      \"lineRef\" : \"1695\",\n" +
//			"      \"lineRef\" : \"10866\",\n" +
//			"      \"lineRef\" : \"10865\",\n" +
//			"      \"lineRef\" : \"12403\",\n" +
//			"      \"lineRef\" : \"12404\",\n" +
//			"      \"lineRef\" : \"10394\",\n" +
//			"      \"lineRef\" : \"10396\",\n" +
//			"      \"lineRef\" : \"10395\",\n" +
//			"      \"lineRef\" : \"16665\",\n" +
//			"      \"lineRef\" : \"11108\",\n" +
//			"      \"lineRef\" : \"11107\",\n" +
//			"      \"lineRef\" : \"10796\",\n" +
//			"      \"lineRef\" : \"10795\",\n" +
//			"      \"lineRef\" : \"10230\",\n" +
//			"      \"lineRef\" : \"10232\",\n" +
//			"      \"lineRef\" : \"10228\",\n" +
//			"      \"lineRef\" : \"10229\",\n" +
//			"      \"lineRef\" : \"22924\",\n" +
//			"      \"lineRef\" : \"10179\",\n" +
//			"      \"lineRef\" : \"10180\",\n" +
//			"      \"lineRef\" : \"12405\",\n" +
//			"      \"lineRef\" : \"12406\",\n" +
//			"      \"lineRef\" : \"5442\",\n" +
//			"      \"lineRef\" : \"5443\",\n" +
//			"      \"lineRef\" : \"5444\",\n" +
//			"      \"lineRef\" : \"5446\",\n" +
//			"      \"lineRef\" : \"17361\",\n" +
//			"      \"lineRef\" : \"17362\",\n" +
//			"      \"lineRef\" : \"10398\",\n" +
//			"      \"lineRef\" : \"10399\",\n" +
//			"      \"lineRef\" : \"10799\",\n" +
//			"      \"lineRef\" : \"10797\",\n" +
//			"      \"lineRef\" : \"15086\",\n" +
//			"      \"lineRef\" : \"15085\",\n" +
//			"      \"lineRef\" : \"11806\",\n" +
//			"      \"lineRef\" : \"10807\",\n" +
//			"      \"lineRef\" : \"10802\",\n" +
//			"      \"lineRef\" : \"10804\",\n" +
//			"      \"lineRef\" : \"10806\",\n" +
//			"      \"lineRef\" : \"10181\",\n" +
//			"      \"lineRef\" : \"10182\",\n" +
//			"      \"lineRef\" : \"10185\",\n" +
//			"      \"lineRef\" : \"10184\",\n" +
//			"      \"lineRef\" : \"12378\",\n" +
//			"      \"lineRef\" : \"12379\",\n" +
//			"      \"lineRef\" : \"12870\",\n" +
//			"      \"lineRef\" : \"5499\",\n" +
//			"      \"lineRef\" : \"5502\",\n" +
//			"      \"lineRef\" : \"10187\",\n" +
//			"      \"lineRef\" : \"10186\",\n" +
//			"      \"lineRef\" : \"10188\",\n" +
//			"      \"lineRef\" : \"10193\",\n" +
//			"      \"lineRef\" : \"10195\",\n" +
//			"      \"lineRef\" : \"10197\",\n" +
//			"      \"lineRef\" : \"10189\",\n" +
//			"      \"lineRef\" : \"2375\",\n" +
//			"      \"lineRef\" : \"5530\",\n" +
//			"      \"lineRef\" : \"5526\",\n" +
//			"      \"lineRef\" : \"5528\",\n" +
//			"      \"lineRef\" : \"10201\",\n" +
//			"      \"lineRef\" : \"10205\",\n" +
//			"      \"lineRef\" : \"10207\",\n" +
//			"      \"lineRef\" : \"10204\",\n" +
//			"      \"lineRef\" : \"10203\",\n" +
//			"      \"lineRef\" : \"10211\",\n" +
//			"      \"lineRef\" : \"10208\",\n" +
//			"      \"lineRef\" : \"10209\",\n" +
//			"      \"lineRef\" : \"21808\",\n" +
//			"      \"lineRef\" : \"21807\",\n" +
//			"      \"lineRef\" : \"12407\",\n" +
//			"      \"lineRef\" : \"12408\",\n" +
//			"      \"lineRef\" : \"12409\",\n" +
//			"      \"lineRef\" : \"12419\",\n" +
//			"      \"lineRef\" : \"12421\",\n" +
//			"      \"lineRef\" : \"10403\",\n" +
//			"      \"lineRef\" : \"10400\",\n" +
//			"      \"lineRef\" : \"10402\",\n" +
//			"      \"lineRef\" : \"10401\",\n" +
//			"      \"lineRef\" : \"10411\",\n" +
//			"      \"lineRef\" : \"10404\",\n" +
//			"      \"lineRef\" : \"10406\",\n" +
//			"      \"lineRef\" : \"10408\",\n" +
//			"      \"lineRef\" : \"10407\",\n" +
//			"      \"lineRef\" : \"16601\",\n" +
//			"      \"lineRef\" : \"10239\",\n" +
//			"      \"lineRef\" : \"10238\",\n" +
//			"      \"lineRef\" : \"10235\",\n" +
//			"      \"lineRef\" : \"10237\",\n" +
//			"      \"lineRef\" : \"10236\",\n" +
//			"      \"lineRef\" : \"10242\",\n" +
//			"      \"lineRef\" : \"12856\",\n" +
//			"      \"lineRef\" : \"12422\",\n" +
//			"      \"lineRef\" : \"12425\",\n" +
//			"      \"lineRef\" : \"12424\",\n" +
//			"      \"lineRef\" : \"17370\",\n" +
//			"      \"lineRef\" : \"17371\",\n" +
//			"      \"lineRef\" : \"16611\",\n" +
//			"      \"lineRef\" : \"12380\",\n" +
//			"      \"lineRef\" : \"12382\",\n" +
//			"      \"lineRef\" : \"22122\",\n" +
//			"      \"lineRef\" : \"10416\",\n" +
//			"      \"lineRef\" : \"10419\",\n" +
//			"      \"lineRef\" : \"10418\",\n" +
//			"      \"lineRef\" : \"12411\",\n" +
//			"      \"lineRef\" : \"10420\",\n" +
//			"      \"lineRef\" : \"10422\",\n" +
//			"      \"lineRef\" : \"10488\",\n" +
//			"      \"lineRef\" : \"10489\",\n" +
//			"      \"lineRef\" : \"12412\",\n" +
//			"      \"lineRef\" : \"12413\",\n" +
//			"      \"lineRef\" : \"5638\",\n" +
//			"      \"lineRef\" : \"5639\",\n" +
//			"      \"lineRef\" : \"14587\",\n" +
//			"      \"lineRef\" : \"14569\",\n" +
//			"      \"lineRef\" : \"5650\",\n" +
//			"      \"lineRef\" : \"5652\",\n" +
//			"      \"lineRef\" : \"5661\",\n" +
//			"      \"lineRef\" : \"5663\",\n" +
//			"      \"lineRef\" : \"10429\",\n" +
//			"      \"lineRef\" : \"12433\",\n" +
//			"      \"lineRef\" : \"7596\",\n" +
//			"      \"lineRef\" : \"12376\",\n" +
//			"      \"lineRef\" : \"10491\",\n" +
//			"      \"lineRef\" : \"10490\",\n" +
//			"      \"lineRef\" : \"20447\",\n" +
//			"      \"lineRef\" : \"20446\",\n" +
//			"      \"lineRef\" : \"10431\",\n" +
//			"      \"lineRef\" : \"10433\",\n" +
//			"      \"lineRef\" : \"10432\",\n" +
//			"      \"lineRef\" : \"10434\",\n" +
//			"      \"lineRef\" : \"12386\",\n" +
//			"      \"lineRef\" : \"10437\",\n" +
//			"      \"lineRef\" : \"10436\",\n" +
//			"      \"lineRef\" : \"10435\",\n" +
//			"      \"lineRef\" : \"10439\",\n" +
//			"      \"lineRef\" : \"10440\",\n" +
//			"      \"lineRef\" : \"10442\",\n" +
//			"      \"lineRef\" : \"10441\",\n" +
//			"      \"lineRef\" : \"22123\",\n" +
//			"      \"lineRef\" : \"10450\",\n" +
//			"      \"lineRef\" : \"10449\",\n" +
//			"      \"lineRef\" : \"10252\",\n" +
//			"      \"lineRef\" : \"10255\",\n" +
//			"      \"lineRef\" : \"12866\",\n" +
//			"      \"lineRef\" : \"10459\",\n" +
//			"      \"lineRef\" : \"10458\",\n" +
//			"      \"lineRef\" : \"10457\",\n" +
//			"      \"lineRef\" : \"12391\",\n" +
//			"      \"lineRef\" : \"12390\",\n" +
//			"      \"lineRef\" : \"12388\",\n" +
//			"      \"lineRef\" : \"12389\",\n" +
//			"      \"lineRef\" : \"12387\",\n" +
//			"      \"lineRef\" : \"12416\",\n" +
//			"      \"lineRef\" : \"12414\",\n" +
//			"      \"lineRef\" : \"12415\",\n" +
//			"      \"lineRef\" : \"10461\",\n" +
//			"      \"lineRef\" : \"10463\",\n" +
//			"      \"lineRef\" : \"17367\",\n" +
//			"      \"lineRef\" : \"17363\",\n" +
//			"      \"lineRef\" : \"10811\",\n" +
//			"      \"lineRef\" : \"10812\",\n" +
//			"      \"lineRef\" : \"10213\",\n" +
//			"      \"lineRef\" : \"10214\",\n" +
//			"      \"lineRef\" : \"12434\",\n" +
//			"      \"lineRef\" : \"12435\",\n" +
//			"      \"lineRef\" : \"10464\",\n" +
//			"      \"lineRef\" : \"10466\",\n" +
//			"      \"lineRef\" : \"10467\",\n" +
//			"      \"lineRef\" : \"10471\",\n" +
//			"      \"lineRef\" : \"10472\",\n" +
//			"      \"lineRef\" : \"10469\",\n" +
//			"      \"lineRef\" : \"11395\",\n" +
//			"      \"lineRef\" : \"11394\",\n" +
//			"      \"lineRef\" : \"10475\",\n" +
//			"      \"lineRef\" : \"10474\",\n" +
//			"      \"lineRef\" : \"2060\",\n" +
//			"      \"lineRef\" : \"10477\",\n" +
//			"      \"lineRef\" : \"10476\",\n" +
//			"      \"lineRef\" : \"12428\",\n" +
//			"      \"lineRef\" : \"12374\",\n" +
//			"      \"lineRef\" : \"12392\",\n" +
//			"      \"lineRef\" : \"12393\",\n" +
//			"      \"lineRef\" : \"12394\",\n" +
//			"      \"lineRef\" : \"16278\",\n" +
//			"      \"lineRef\" : \"21642\",\n";
//}
