#!/usr/bin/env python3
"""
Cricket Head-to-Head Statistics Calculator
Calculates win/loss records between Prasanna Nivas and opponents from tournament data
"""

import json
import os
from collections import defaultdict
from datetime import datetime
import csv


class CricketHeadToHead:
    def __init__(self):
        self.player_name = "Prasanna Nivas"
        self.player_id = "7899a991-fffd-495f-851e-fc5afa366356"
        self.data = []
        self.head_to_head_stats = defaultdict(
            lambda: {"wins": 0, "losses": 0, "total_matches": 0})
        self.tournament_stats = defaultdict(lambda: defaultdict(
            lambda: {"wins": 0, "losses": 0, "total_matches": 0}))
        self.tournament_types = set()

    def load_data(self, file_paths):
        """Load data from multiple JSON files"""
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'match_details' in data:
                            self.data.extend(data['match_details'])
                            print(
                                f"✓ Loaded {len(data['match_details'])} matches from {file_path}")
                        else:
                            print(f"⚠ No match_details found in {file_path}")
                except json.JSONDecodeError as e:
                    print(f"✗ Error reading {file_path}: {e}")
                except Exception as e:
                    print(f"✗ Error loading {file_path}: {e}")
            else:
                print(f"✗ File not found: {file_path}")

    def parse_tournament_type(self, tournament_name):
        """Parse tournament type from tournament name"""
        if not tournament_name:
            return "Other", "Unknown"

        # Extract main tournament type and subtype
        if "iBC PRO 360" in tournament_name:
            main_type = "iBC PRO 360"
            # Extract the number (250, 500, 1000, etc.)
            parts = tournament_name.split(" - ")
            if len(parts) > 1:
                subtype_part = parts[1].split(" ")[0]
                subtype = f"iBC PRO 360 - {subtype_part}"
            else:
                subtype = "iBC PRO 360 - Unknown"
        elif "iBC 360" in tournament_name:
            main_type = "iBC 360"
            # Extract the number (250, 500, 1000, etc.)
            parts = tournament_name.split(" - ")
            if len(parts) > 1:
                subtype_part = parts[1].split(" ")[0]
                subtype = f"iBC 360 - {subtype_part}"
            else:
                subtype = "iBC 360 - Unknown"
        else:
            main_type = "Other"
            subtype = tournament_name

        return main_type, subtype

    def calculate_head_to_head(self):
        """Calculate head-to-head statistics against all opponents"""
        for match in self.data:
            # Only process completed dual-player matches
            if (match.get('status') != 'COMPLETED' or
                    match.get('match_mode') != 'DUAL_PLAYER'):
                continue

            match_user_details = match.get('match_user_details', {})
            users = match_user_details.get('users', [])

            # Find myself and opponent in the match
            myself = None
            opponent = None

            for user in users:
                if user.get('user_id') == self.player_id:
                    myself = user
                else:
                    opponent = user

            # Skip if I'm not in the match or no opponent found
            if not myself or not opponent:
                continue

            opponent_name = opponent.get('name', 'Unknown')
            my_result = myself.get('result')
            tournament_name = match.get('tournament_name', 'Unknown')
            main_type, subtype = self.parse_tournament_type(tournament_name)

            # Track tournament types
            self.tournament_types.add(main_type)

            # Update overall statistics
            self.head_to_head_stats[opponent_name]["total_matches"] += 1

            # Update tournament-specific statistics
            self.tournament_stats[main_type][opponent_name]["total_matches"] += 1
            self.tournament_stats[subtype][opponent_name]["total_matches"] += 1

            if my_result == 'WIN':
                self.head_to_head_stats[opponent_name]["wins"] += 1
                self.tournament_stats[main_type][opponent_name]["wins"] += 1
                self.tournament_stats[subtype][opponent_name]["wins"] += 1
            elif my_result == 'LOSS':
                self.head_to_head_stats[opponent_name]["losses"] += 1
                self.tournament_stats[main_type][opponent_name]["losses"] += 1
                self.tournament_stats[subtype][opponent_name]["losses"] += 1

    def print_statistics(self, tournament_filter="All"):
        """Print head-to-head statistics in a formatted table"""
        if tournament_filter == "All":
            stats_data = self.head_to_head_stats
            title = f"🏏 HEAD-TO-HEAD STATISTICS FOR {self.player_name.upper()} - ALL TOURNAMENTS 🏏"
        else:
            stats_data = self.tournament_stats.get(tournament_filter, {})
            title = f"🏏 HEAD-TO-HEAD STATISTICS FOR {self.player_name.upper()} - {tournament_filter.upper()} 🏏"

        if not stats_data:
            print(f"No head-to-head data found for {tournament_filter}!")
            return

        print(f"\n{'='*80}")
        print(title)
        print(f"{'='*80}")

        # Sort opponents by total matches (descending)
        sorted_opponents = sorted(
            stats_data.items(),
            key=lambda x: x[1]['total_matches'],
            reverse=True
        )

        print(f"{'OPPONENT':<25} {'WINS':<6} {'LOSSES':<8} {'TOTAL':<8} {'WIN %':<8}")
        print(f"{'-'*80}")

        total_wins = 0
        total_losses = 0
        total_matches = 0

        for opponent, stats in sorted_opponents:
            wins = stats['wins']
            losses = stats['losses']
            total = stats['total_matches']
            win_percentage = (wins / total * 100) if total > 0 else 0

            # Truncate long opponent names
            display_name = opponent[:24] if len(opponent) > 24 else opponent

            print(
                f"{display_name:<25} {wins:<6} {losses:<8} {total:<8} {win_percentage:<7.1f}%")

            total_wins += wins
            total_losses += losses
            total_matches += total

        print(f"{'-'*80}")
        overall_win_percentage = (
            total_wins / total_matches * 100) if total_matches > 0 else 0
        print(f"{'OVERALL':<25} {total_wins:<6} {total_losses:<8} {total_matches:<8} {overall_win_percentage:<7.1f}%")
        print(f"{'='*80}")

        return {
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_matches': total_matches,
            'win_percentage': overall_win_percentage,
            'opponents_data': sorted_opponents
        }

    def _get_statistics_data(self, tournament_filter="All"):
        """Get statistics data without printing"""
        if tournament_filter == "All":
            stats_data = self.head_to_head_stats
        else:
            stats_data = self.tournament_stats.get(tournament_filter, {})

        if not stats_data:
            return {
                'total_wins': 0,
                'total_losses': 0,
                'total_matches': 0,
                'win_percentage': 0,
                'opponents_data': []
            }

        # Sort opponents by total matches (descending)
        sorted_opponents = sorted(
            stats_data.items(),
            key=lambda x: x[1]['total_matches'],
            reverse=True
        )

        total_wins = 0
        total_losses = 0
        total_matches = 0

        for opponent, stats in sorted_opponents:
            total_wins += stats['wins']
            total_losses += stats['losses']
            total_matches += stats['total_matches']

        overall_win_percentage = (
            total_wins / total_matches * 100) if total_matches > 0 else 0

        return {
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_matches': total_matches,
            'win_percentage': overall_win_percentage,
            'opponents_data': sorted_opponents
        }

    def get_detailed_stats(self, opponent_name=None):
        """Get detailed statistics for a specific opponent or all opponents"""
        if opponent_name:
            if opponent_name in self.head_to_head_stats:
                stats = self.head_to_head_stats[opponent_name]
                print(f"\n📊 DETAILED STATS vs {opponent_name}:")
                print(f"   Wins: {stats['wins']}")
                print(f"   Losses: {stats['losses']}")
                print(f"   Total Matches: {stats['total_matches']}")
                if stats['total_matches'] > 0:
                    win_rate = (stats['wins'] / stats['total_matches'] * 100)
                    print(f"   Win Rate: {win_rate:.1f}%")
            else:
                print(f"No data found for opponent: {opponent_name}")
        else:
            return dict(self.head_to_head_stats)

    def find_best_opponent(self):
        """Find the opponent with best win rate (minimum 2 matches)"""
        best_opponent = None
        best_win_rate = -1

        for opponent, stats in self.head_to_head_stats.items():
            if stats['total_matches'] >= 2:  # At least 2 matches
                win_rate = stats['wins'] / stats['total_matches']
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_opponent = opponent

        if best_opponent:
            print(f"\n🎯 BEST MATCHUP: {best_opponent}")
            print(
                f"   Win Rate: {best_win_rate*100:.1f}% ({self.head_to_head_stats[best_opponent]['wins']} wins out of {self.head_to_head_stats[best_opponent]['total_matches']} matches)")

    def find_toughest_opponent(self):
        """Find the opponent with worst win rate (minimum 2 matches)"""
        toughest_opponent = None
        worst_win_rate = 2.0  # Start with impossible value

        for opponent, stats in self.head_to_head_stats.items():
            if stats['total_matches'] >= 2:  # At least 2 matches
                win_rate = stats['wins'] / stats['total_matches']
                if win_rate < worst_win_rate:
                    worst_win_rate = win_rate
                    toughest_opponent = opponent

        if toughest_opponent:
            print(f"\n⚔️ TOUGHEST OPPONENT: {toughest_opponent}")
            print(
                f"   Win Rate: {worst_win_rate*100:.1f}% ({self.head_to_head_stats[toughest_opponent]['wins']} wins out of {self.head_to_head_stats[toughest_opponent]['total_matches']} matches)")

    def generate_html_report(self, filename="cricket_report.html"):
        """Generate comprehensive HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cricket Head-to-Head Report - {self.player_name}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .tournament-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
        }}
        .tournament-section h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #34495e;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4fd;
        }}
        .win-rate {{
            font-weight: bold;
        }}
        .win-rate.high {{
            color: #27ae60;
        }}
        .win-rate.medium {{
            color: #f39c12;
        }}
        .win-rate.low {{
            color: #e74c3c;
        }}
        .insights {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .insights h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .filter-tabs {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #e74c3c;
        }}
        .filter-tab {{
            padding: 10px 20px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            margin-right: 5px;
            border-radius: 5px 5px 0 0;
        }}
        .filter-tab.active {{
            background: #e74c3c;
            color: white;
        }}
        .content-section {{
            display: none;
        }}
        .content-section.active {{
            display: block;
        }}
    </style>
    <script>
        function showSection(sectionId) {{
            // Hide all sections
            var sections = document.querySelectorAll('.content-section');
            sections.forEach(function(section) {{
                section.classList.remove('active');
            }});
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Update tab styling
            var tabs = document.querySelectorAll('.filter-tab');
            tabs.forEach(function(tab) {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏏 Cricket Head-to-Head Analysis Report</h1>
            <h2>{self.player_name}</h2>
            <p>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
"""

        # Generate overall summary
        all_stats = self._get_statistics_data("All")

        html_content += f"""
        <div class="summary-cards">
            <div class="card">
                <h3>Total Matches</h3>
                <div class="value">{all_stats['total_matches']}</div>
            </div>
            <div class="card">
                <h3>Total Wins</h3>
                <div class="value">{all_stats['total_wins']}</div>
            </div>
            <div class="card">
                <h3>Total Losses</h3>
                <div class="value">{all_stats['total_losses']}</div>
            </div>
            <div class="card">
                <h3>Win Rate</h3>
                <div class="value">{all_stats['win_percentage']:.1f}%</div>
            </div>
        </div>

        <div class="filter-tabs">
            <button class="filter-tab active" onclick="showSection('all-tournaments')">All Tournaments</button>
            <button class="filter-tab" onclick="showSection('ibc-pro-360')">iBC PRO 360</button>
            <button class="filter-tab" onclick="showSection('ibc-360')">iBC 360</button>
        </div>
"""

        # All tournaments section
        html_content += f"""
        <div id="all-tournaments" class="content-section active">
            <div class="tournament-section">
                <h2>📊 All Tournaments - Head-to-Head Statistics</h2>
                {self._generate_table_html(all_stats['opponents_data'])}
            </div>
        </div>
"""

        # iBC PRO 360 section
        pro_360_stats = self._get_statistics_data("iBC PRO 360")
        html_content += f"""
        <div id="ibc-pro-360" class="content-section">
            <div class="tournament-section">
                <h2>🏆 iBC PRO 360 Tournaments</h2>
                <div class="summary-cards">
                    <div class="card">
                        <h3>Matches</h3>
                        <div class="value">{pro_360_stats['total_matches']}</div>
                    </div>
                    <div class="card">
                        <h3>Wins</h3>
                        <div class="value">{pro_360_stats['total_wins']}</div>
                    </div>
                    <div class="card">
                        <h3>Win Rate</h3>
                        <div class="value">{pro_360_stats['win_percentage']:.1f}%</div>
                    </div>
                </div>
                {self._generate_table_html(pro_360_stats['opponents_data'])}
            </div>
        </div>
"""

        # iBC 360 section
        bc_360_stats = self._get_statistics_data("iBC 360")
        html_content += f"""
        <div id="ibc-360" class="content-section">
            <div class="tournament-section">
                <h2>🎯 iBC 360 Tournaments</h2>
                <div class="summary-cards">
                    <div class="card">
                        <h3>Matches</h3>
                        <div class="value">{bc_360_stats['total_matches']}</div>
                    </div>
                    <div class="card">
                        <h3>Wins</h3>
                        <div class="value">{bc_360_stats['total_wins']}</div>
                    </div>
                    <div class="card">
                        <h3>Win Rate</h3>
                        <div class="value">{bc_360_stats['win_percentage']:.1f}%</div>
                    </div>
                </div>
                {self._generate_table_html(bc_360_stats['opponents_data'])}
            </div>
        </div>
"""

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML report generated: {filename}")

    def _generate_table_html(self, opponents_data):
        """Generate HTML table for opponents data"""
        if not opponents_data:
            return "<p>No data available</p>"

        table_html = """
        <table>
            <thead>
                <tr>
                    <th>Opponent</th>
                    <th>Wins</th>
                    <th>Losses</th>
                    <th>Total</th>
                    <th>Win Rate</th>
                </tr>
            </thead>
            <tbody>
"""

        for opponent, stats in opponents_data:
            wins = stats['wins']
            losses = stats['losses']
            total = stats['total_matches']
            win_percentage = (wins / total * 100) if total > 0 else 0

            # Color coding for win rate
            if win_percentage >= 70:
                rate_class = "high"
            elif win_percentage >= 40:
                rate_class = "medium"
            else:
                rate_class = "low"

            table_html += f"""
                <tr>
                    <td>{opponent}</td>
                    <td>{wins}</td>
                    <td>{losses}</td>
                    <td>{total}</td>
                    <td class="win-rate {rate_class}">{win_percentage:.1f}%</td>
                </tr>
"""

        table_html += """
            </tbody>
        </table>
"""
        return table_html

    def generate_csv_report(self, filename="cricket_report.csv"):
        """Generate CSV report for data analysis"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Tournament_Type', 'Opponent', 'Wins',
                            'Losses', 'Total_Matches', 'Win_Percentage'])

            # Write All tournaments data
            for opponent, stats in self.head_to_head_stats.items():
                win_percentage = (
                    stats['wins'] / stats['total_matches'] * 100) if stats['total_matches'] > 0 else 0
                writer.writerow(['All', opponent, stats['wins'], stats['losses'],
                                stats['total_matches'], f"{win_percentage:.1f}"])

            # Write tournament-specific data
            for tournament_type, opponents_data in self.tournament_stats.items():
                for opponent, stats in opponents_data.items():
                    win_percentage = (
                        stats['wins'] / stats['total_matches'] * 100) if stats['total_matches'] > 0 else 0
                    writer.writerow([tournament_type, opponent, stats['wins'],
                                    stats['losses'], stats['total_matches'], f"{win_percentage:.1f}"])

        print(f"✅ CSV report generated: {filename}")

    def get_tournament_subtypes(self, main_type):
        """Get all subtypes for a main tournament type"""
        subtypes = []
        for tournament_type in self.tournament_stats.keys():
            if tournament_type.startswith(main_type) and " - " in tournament_type:
                subtypes.append(tournament_type)
        return sorted(subtypes)


def main():
    """Main function to run the head-to-head analysis"""
    print("🏏 Cricket Head-to-Head Statistics Calculator with Tournament Filters")
    print("=" * 70)

    # Initialize calculator
    calculator = CricketHeadToHead()

    # Data file paths
    data_files = [
        "data/tournament1.json",
        "data/tournament2.json"
    ]

    # Load data from files
    print("\n📂 Loading tournament data...")
    calculator.load_data(data_files)

    if not calculator.data:
        print("❌ No data loaded! Please check your data files.")
        return

    print(f"\n✅ Total matches loaded: {len(calculator.data)}")

    # Calculate head-to-head statistics
    print("\n🔄 Calculating head-to-head statistics...")
    calculator.calculate_head_to_head()

    # Display results for all tournaments
    print("\n" + "="*80)
    print("📊 GENERATING COMPREHENSIVE REPORTS")
    print("="*80)

    # Display overall statistics
    all_stats = calculator.print_statistics("All")

    # Display tournament-specific statistics
    print("\n" + "="*60)
    print("🏆 iBC PRO 360 TOURNAMENTS")
    print("="*60)
    pro_stats = calculator.print_statistics("iBC PRO 360")

    print("\n" + "="*60)
    print("🎯 iBC 360 TOURNAMENTS")
    print("="*60)
    bc_stats = calculator.print_statistics("iBC 360")

    # Show detailed subtypes
    print("\n" + "="*60)
    print("📋 DETAILED SUBTYPE ANALYSIS")
    print("="*60)

    # Get all tournament subtypes
    pro_subtypes = calculator.get_tournament_subtypes("iBC PRO 360")
    bc_subtypes = calculator.get_tournament_subtypes("iBC 360")

    print(f"\n🏆 iBC PRO 360 Subtypes found: {len(pro_subtypes)}")
    for subtype in pro_subtypes:
        if calculator.tournament_stats[subtype]:
            subtype_stats = calculator.print_statistics(subtype)
            print()

    print(f"\n🎯 iBC 360 Subtypes found: {len(bc_subtypes)}")
    for subtype in bc_subtypes:
        if calculator.tournament_stats[subtype]:
            subtype_stats = calculator.print_statistics(subtype)
            print()

    # Show additional insights
    calculator.find_best_opponent()
    calculator.find_toughest_opponent()

    # Generate reports
    print("\n" + "="*60)
    print("📝 GENERATING REPORTS")
    print("="*60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate HTML report
    html_filename = f"cricket_report_{timestamp}.html"
    calculator.generate_html_report(html_filename)

    # Generate CSV report
    csv_filename = f"cricket_report_{timestamp}.csv"
    calculator.generate_csv_report(csv_filename)

    print(f"\n🎉 Analysis complete!")
    print(f"📊 Tournament types found: {list(calculator.tournament_types)}")
    print(
        f"📅 Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Files created:")
    print(f"   📄 HTML Report: {html_filename}")
    print(f"   📊 CSV Report: {csv_filename}")

    # Summary statistics
    print(f"\n📈 SUMMARY:")
    print(f"   Total Opponents: {len(calculator.head_to_head_stats)}")
    print(f"   Overall Win Rate: {all_stats['win_percentage']:.1f}%")
    print(f"   iBC PRO 360 Win Rate: {pro_stats['win_percentage']:.1f}%")
    print(f"   iBC 360 Win Rate: {bc_stats['win_percentage']:.1f}%")


if __name__ == "__main__":
    main()
