import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:fl_chart/fl_chart.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ERP Dashboard',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int uretim = 0;
  int stok = 0;
  String hataMesaji = '';
  Timer? timer;

  Future<void> fetchVeri() async {
    try {
      final response = await http.get(Uri.parse('http://192.168.1.194:5000/veri'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          uretim = data['uretim'] ?? 0;
          stok = data['stok'] ?? 0;
          hataMesaji = '';
        });
      } else {
        throw Exception('Sunucu hatası: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        hataMesaji = 'Bağlantı hatası:\n$e';
      });
    }
  }

  @override
  void initState() {
    super.initState();
    fetchVeri();
    timer = Timer.periodic(const Duration(seconds: 2), (_) => fetchVeri());
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void goToLogScreen() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LogScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("ERP Paneli – Canlı Üretim Takibi"),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.indigo, Colors.blueAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const Icon(Icons.factory_rounded, size: 60, color: Colors.indigo),
                const SizedBox(height: 20),
                Card(
                  elevation: 6,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        Text("Üretim Sayısı", style: Theme.of(context).textTheme.titleLarge),
                        const SizedBox(height: 8),
                        Text(
                          "$uretim",
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 24),
                        Text("Kalan Stok", style: Theme.of(context).textTheme.titleLarge),
                        const SizedBox(height: 8),
                        Text(
                          "$stok",
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 24),
                        if (stok == 0)
                          const Text("Stok tükendi!",
                              style: TextStyle(fontSize: 18, color: Colors.red)),
                        if (stok > 0 && stok <= 2)
                          const Text("Stok azaldı, sipariş gerekli!",
                              style: TextStyle(fontSize: 18, color: Colors.orange)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                if (hataMesaji.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(top: 10),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      border: Border.all(color: Colors.red),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(hataMesaji,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center),
                  ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: goToLogScreen,
                  icon: const Icon(Icons.timeline),
                  label: const Text("Geçmiş & Grafik"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.indigo,
                    foregroundColor: Colors.white,
                    minimumSize: const Size(180, 48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                const Text("Veriler 2 saniyede bir güncelleniyor...",
                    style: TextStyle(fontSize: 14, color: Colors.grey)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// LOG SCREEN

class LogScreen extends StatefulWidget {
  const LogScreen({super.key});

  @override
  State<LogScreen> createState() => _LogScreenState();
}

class _LogScreenState extends State<LogScreen> {
  List<dynamic> logData = [];
  bool loading = true;

  Future<void> fetchLog() async {
    try {
      final response = await http.get(Uri.parse("http://192.168.1.194:5000/log"));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          logData = data;
          loading = false;
        });
      } else {
        throw Exception("Log verisi alınamadı.");
      }
    } catch (e) {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    fetchLog();
  }

  @override
  Widget build(BuildContext context) {
    List<FlSpot> uretimSpots = [];
    List<FlSpot> stokSpots = [];

    for (int i = 0; i < logData.length; i++) {
      final item = logData[i];
      final double uretim = double.tryParse(item["Üretim"].toString()) ?? 0;
      final double stok = double.tryParse(item["Stok"].toString()) ?? 0;
      uretimSpots.add(FlSpot(i.toDouble(), uretim));
      stokSpots.add(FlSpot(i.toDouble(), stok));
    }

    double ortUretim = logData.isEmpty
        ? 0
        : logData.map((e) => double.tryParse(e["Üretim"].toString()) ?? 0).reduce((a, b) => a + b) / logData.length;
    double ortStok = logData.isEmpty
        ? 0
        : logData.map((e) => double.tryParse(e["Stok"].toString()) ?? 0).reduce((a, b) => a + b) / logData.length;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Üretim & Stok Geçmişi"),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            const SizedBox(height: 10),
            const Text("Zaman Serisi Grafiği", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(
              height: 220,
              child: logData.length < 2
                  ? const Center(child: Text("Grafik için yeterli veri yok."))
                  : LineChart(
                LineChartData(
                  lineBarsData: [
                    LineChartBarData(
                      spots: uretimSpots,
                      isCurved: true,
                      color: Colors.blue,
                      barWidth: 3,
                      dotData: FlDotData(show: false),
                    ),
                    LineChartBarData(
                      spots: stokSpots,
                      isCurved: true,
                      color: Colors.green,
                      barWidth: 3,
                      dotData: FlDotData(show: false),
                    ),
                  ],
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                  ),
                  borderData: FlBorderData(show: true),
                  gridData: FlGridData(show: true),
                ),
              ),
            ),
            const SizedBox(height: 18),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Text("Ortalama Üretim: ${ortUretim.toStringAsFixed(1)}"),
                Text("Ortalama Stok: ${ortStok.toStringAsFixed(1)}"),
              ],
            ),
            const SizedBox(height: 20),
            const Divider(),
            const Text("Son 10 Kayıt", style: TextStyle(fontWeight: FontWeight.bold)),
            Expanded(
              child: ListView.builder(
                itemCount: logData.length > 10 ? 10 : logData.length,
                itemBuilder: (context, idx) {
                  final item = logData[logData.length - 1 - idx];
                  return ListTile(
                    leading: const Icon(Icons.history),
                    title: Text("Zaman: ${item["Zaman"]}"),
                    subtitle: Text("Üretim: ${item["Üretim"]} | Stok: ${item["Stok"]}"),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
