#!/usr/bin/env python3
"""
Enhanced Cricket Head-to-Head Report Generator with Tournament Filters
"""

import json
import os
from collections import defaultdict
from datetime import datetime
import csv


class CricketReportGenerator:
    def __init__(self):
        self.player_name = "Prasanna Nivas"
        self.player_id = "7899a991-fffd-495f-851e-fc5afa366356"
        self.player_pic_url = ""
        self.data = []
        self.head_to_head_stats = defaultdict(
            lambda: {"wins": 0, "losses": 0, "total_matches": 0})
        self.tournament_stats = defaultdict(lambda: defaultdict(
            lambda: {"wins": 0, "losses": 0, "total_matches": 0}))
        self.tournament_types = set()
        self.opponent_pics = {}  # Store opponent profile pictures

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
                except Exception as e:
                    print(f"✗ Error loading {file_path}: {e}")
            else:
                print(f"✗ File not found: {file_path}")

    def parse_tournament_type(self, tournament_name):
        """Parse tournament type from tournament name"""
        if not tournament_name:
            return "Other", "Unknown"

        if "iBC PRO 360" in tournament_name:
            main_type = "iBC PRO 360"
            parts = tournament_name.split(" - ")
            if len(parts) > 1:
                subtype_part = parts[1].split(" ")[0]
                subtype = f"iBC PRO 360 - {subtype_part}"
            else:
                subtype = "iBC PRO 360 - Unknown"
        elif "iBC 360" in tournament_name and "iBC PRO 360" not in tournament_name:
            main_type = "iBC 360"
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

    def calculate_statistics(self):
        """Calculate head-to-head statistics"""
        print("\n🔄 Processing matches...")
        processed = 0

        for match in self.data:
            if (match.get('status') != 'COMPLETED' or
                    match.get('match_mode') != 'DUAL_PLAYER'):
                continue

            match_user_details = match.get('match_user_details', {})
            users = match_user_details.get('users', [])

            myself = None
            opponent = None

            for user in users:
                if user.get('user_id') == self.player_id:
                    myself = user
                else:
                    opponent = user

            if not myself or not opponent:
                continue

            opponent_name = opponent.get('name', 'Unknown')
            my_result = myself.get('result')

            # Store profile pictures
            if not self.player_pic_url:
                self.player_pic_url = myself.get('pic_url', '')

            opponent_pic_url = opponent.get('pic_url', '')
            if opponent_name not in self.opponent_pics:
                self.opponent_pics[opponent_name] = opponent_pic_url

            # Get tournament name from tournament_match_details
            tournament_match_details = match.get(
                'tournament_match_details', {})
            tournament_type_details = tournament_match_details.get(
                'tournament_type_details', {})
            tournament_name = tournament_type_details.get(
                'tournament_name', 'Unknown')

            main_type, subtype = self.parse_tournament_type(tournament_name)

            self.tournament_types.add(main_type)

            # Update statistics
            self.head_to_head_stats[opponent_name]["total_matches"] += 1
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

            processed += 1

        print(f"✅ Processed {processed} matches successfully")

    def get_statistics_summary(self, tournament_filter="All"):
        """Get statistics summary for a tournament filter"""
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
                'opponents_count': 0,
                'top_opponents': []
            }

        total_wins = sum(stats['wins'] for stats in stats_data.values())
        total_losses = sum(stats['losses'] for stats in stats_data.values())
        total_matches = sum(stats['total_matches']
                            for stats in stats_data.values())
        win_percentage = (total_wins / total_matches *
                          100) if total_matches > 0 else 0

        # Top opponents (by number of matches)
        top_opponents = sorted(
            [(name, stats) for name, stats in stats_data.items()],
            key=lambda x: x[1]['total_matches'],
            reverse=True
        )[:10]

        return {
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_matches': total_matches,
            'win_percentage': win_percentage,
            'opponents_count': len(stats_data),
            'top_opponents': top_opponents
        }

    def print_tournament_summary(self, tournament_filter="All"):
        """Print summary for a specific tournament filter"""
        summary = self.get_statistics_summary(tournament_filter)

        if summary['total_matches'] == 0:
            print(f"\n❌ No matches found for {tournament_filter}")
            return summary

        print(f"\n{'='*60}")
        print(f"📊 {tournament_filter.upper()} TOURNAMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Matches: {summary['total_matches']}")
        print(f"Total Wins: {summary['total_wins']}")
        print(f"Total Losses: {summary['total_losses']}")
        print(f"Win Rate: {summary['win_percentage']:.1f}%")
        print(f"Unique Opponents: {summary['opponents_count']}")

        print(f"\n🏆 TOP 10 MOST FACED OPPONENTS:")
        print(f"{'Opponent':<25} {'W':<4} {'L':<4} {'Total':<6} {'Win%':<8}")
        print("-" * 55)

        for opponent, stats in summary['top_opponents']:
            wins = stats['wins']
            losses = stats['losses']
            total = stats['total_matches']
            win_rate = (wins / total * 100) if total > 0 else 0

            display_name = opponent[:24] if len(opponent) > 24 else opponent
            print(
                f"{display_name:<25} {wins:<4} {losses:<4} {total:<6} {win_rate:<7.1f}%")

        return summary

    def generate_detailed_report(self):
        """Generate detailed text report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cricket_detailed_report_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(
                f"🏏 CRICKET HEAD-TO-HEAD DETAILED REPORT - {self.player_name.upper()}\n")
            f.write("="*80 + "\n")
            f.write(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
            f.write("="*80 + "\n\n")

            # Overall summary
            all_summary = self.get_statistics_summary("All")
            f.write("📋 OVERALL SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Matches: {all_summary['total_matches']}\n")
            f.write(f"Total Wins: {all_summary['total_wins']}\n")
            f.write(f"Total Losses: {all_summary['total_losses']}\n")
            f.write(
                f"Overall Win Rate: {all_summary['win_percentage']:.1f}%\n")
            f.write(f"Unique Opponents: {all_summary['opponents_count']}\n\n")

            # Tournament type summaries
            for tournament_type in ['iBC PRO 360', 'iBC 360', 'Other']:
                summary = self.get_statistics_summary(tournament_type)
                if summary['total_matches'] > 0:
                    f.write(f"🏆 {tournament_type.upper()} SUMMARY\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Matches: {summary['total_matches']}\n")
                    f.write(f"Wins: {summary['total_wins']}\n")
                    f.write(f"Losses: {summary['total_losses']}\n")
                    f.write(f"Win Rate: {summary['win_percentage']:.1f}%\n")
                    f.write(f"Opponents: {summary['opponents_count']}\n\n")

            # Detailed opponent breakdown for all tournaments
            f.write("📊 DETAILED OPPONENT BREAKDOWN (ALL TOURNAMENTS)\n")
            f.write("-" * 60 + "\n")
            f.write(
                f"{'Opponent':<30} {'W':<5} {'L':<5} {'Total':<7} {'Win%':<8}\n")
            f.write("-" * 60 + "\n")

            sorted_opponents = sorted(
                self.head_to_head_stats.items(),
                key=lambda x: x[1]['total_matches'],
                reverse=True
            )

            for opponent, stats in sorted_opponents:
                wins = stats['wins']
                losses = stats['losses']
                total = stats['total_matches']
                win_rate = (wins / total * 100) if total > 0 else 0
                f.write(
                    f"{opponent[:29]:<30} {wins:<5} {losses:<5} {total:<7} {win_rate:<7.1f}%\n")

        print(f"✅ Detailed report generated: {filename}")
        return filename

    def generate_csv_export(self):
        """Generate CSV export for data analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cricket_data_export_{timestamp}.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Tournament_Type', 'Opponent', 'Wins',
                            'Losses', 'Total_Matches', 'Win_Percentage'])

            # All tournaments data
            for opponent, stats in self.head_to_head_stats.items():
                win_percentage = (
                    stats['wins'] / stats['total_matches'] * 100) if stats['total_matches'] > 0 else 0
                writer.writerow(['All', opponent, stats['wins'], stats['losses'],
                                stats['total_matches'], f"{win_percentage:.1f}"])

            # Tournament-specific data
            for tournament_type, opponents_data in self.tournament_stats.items():
                for opponent, stats in opponents_data.items():
                    win_percentage = (
                        stats['wins'] / stats['total_matches'] * 100) if stats['total_matches'] > 0 else 0
                    writer.writerow([tournament_type, opponent, stats['wins'],
                                    stats['losses'], stats['total_matches'], f"{win_percentage:.1f}"])

        print(f"✅ CSV export generated: {filename}")
        return filename

    def generate_html_report(self):
        """Generate comprehensive HTML report with premium UI design"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cricket_premium_report_{timestamp}.html"

        # Get overall statistics
        all_summary = self.get_statistics_summary("All")
        pro_summary = self.get_statistics_summary("iBC PRO 360")
        bc_summary = self.get_statistics_summary("iBC 360")

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cricket Performance Analytics - {self.player_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e1a;
            color: #f8fafc;
            line-height: 1.6;
            overflow-x: hidden;
        }}
        
        .background-pattern {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 200, 255, 0.2) 0%, transparent 50%);
            z-index: -1;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .glass-card {{
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }}
        
        .header {{
            text-align: center;
            padding: 60px 40px;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(99, 102, 241, 0.1) 0%, 
                rgba(168, 85, 247, 0.1) 50%, 
                rgba(236, 72, 153, 0.1) 100%);
            z-index: -1;
        }}
        
        .header h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            letter-spacing: -0.02em;
        }}
        
        .player-profile {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
        }}
        
        .player-avatar {{
            position: relative;
            width: 80px;
            height: 80px;
        }}
        
        .player-avatar img, .player-avatar .default-avatar {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 3px solid #6366f1;
            object-fit: cover;
        }}
        
        .player-avatar::after {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            border-radius: 50%;
            background: linear-gradient(45deg, #6366f1, #a855f7, #ec4899);
            z-index: -1;
            animation: rotate 3s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .player-name {{
            font-size: 2rem;
            font-weight: 600;
            color: #f1f5f9;
            margin: 0;
        }}
        
        .timestamp {{
            color: #94a3b8;
            font-size: 1rem;
            font-weight: 400;
            margin-top: 10px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 50px;
        }}
        
        .metric-card {{
            padding: 32px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .metric-card:hover {{
            transform: translateY(-8px);
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }}
        
        .metric-icon {{
            font-size: 2.5rem;
            margin-bottom: 16px;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 3rem;
            font-weight: 700;
            color: #f1f5f9;
            line-height: 1;
            margin-bottom: 8px;
        }}
        
        .metric-subtitle {{
            font-size: 0.75rem;
            color: #64748b;
            font-weight: 400;
        }}
        
        .navigation {{
            display: flex;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 16px;
            padding: 8px;
            margin-bottom: 40px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .nav-tab {{
            flex: 1;
            padding: 16px 24px;
            background: transparent;
            color: #94a3b8;
            border: none;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .nav-tab:hover {{
            color: #f1f5f9;
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .nav-tab.active {{
            color: #f1f5f9;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            box-shadow: 
                0 4px 12px rgba(99, 102, 241, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }}
        
        .content-section {{
            display: none;
        }}
        
        .content-section.active {{
            display: block;
        }}
        
        .tournament-content {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 2rem;
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        
        .data-table thead th {{
            background: rgba(15, 23, 42, 0.8);
            padding: 20px 16px;
            text-align: left;
            font-weight: 600;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .data-table tbody td {{
            padding: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.2s ease;
        }}
        
        .data-table tbody tr {{
            transition: all 0.2s ease;
        }}
        
        .data-table tbody tr:hover {{
            background: rgba(255, 255, 255, 0.08);
        }}
        
        .player-matchup {{
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 180px;
        }}
        
        .avatar-container {{
            position: relative;
            width: 40px;
            height: 40px;
        }}
        
        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #475569;
        }}
        
        .avatar-fallback {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.875rem;
            border: 2px solid #475569;
        }}
        
        .vs-indicator {{
            font-size: 0.75rem;
            font-weight: 600;
            color: #6366f1;
            background: rgba(99, 102, 241, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .opponent-name {{
            font-weight: 500;
            color: #f1f5f9;
        }}
        
        .stat-number {{
            font-weight: 600;
            font-size: 1.1rem;
            text-align: center;
        }}
        
        .wins {{ color: #22c55e; }}
        .losses {{ color: #ef4444; }}
        .total {{ color: #f1f5f9; }}
        
        .win-rate-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.875rem;
            text-align: center;
            min-width: 80px;
        }}
        
        .win-rate-high {{
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }}
        
        .win-rate-medium {{
            background: linear-gradient(135deg, #d97706, #f59e0b);
            color: white;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }}
        
        .win-rate-low {{
            background: linear-gradient(135deg, #dc2626, #ef4444);
            color: white;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }}
        
        .loading-state {{
            text-align: center;
            padding: 60px;
            color: #64748b;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px;
            color: #64748b;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 12px; }}
            .header {{ padding: 40px 20px; }}
            .summary-grid {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
            .navigation {{ flex-direction: column; gap: 8px; }}
            .nav-tab {{ text-align: center; }}
            .tournament-content {{ padding: 20px; }}
            .data-table {{ font-size: 0.8rem; }}
            .data-table thead th, .data-table tbody td {{ padding: 12px 8px; }}
        }}
        
        .scroll-indicator {{
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
            z-index: 1000;
            transition: width 0.1s ease;
        }}
    </style>
    <script>
        function showSection(sectionId) {{
            const sections = document.querySelectorAll('.content-section');
            const tabs = document.querySelectorAll('.nav-tab');
            
            sections.forEach(section => section.classList.remove('active'));
            tabs.forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Scroll progress indicator
        window.addEventListener('scroll', () => {{
            const scrolled = window.pageYOffset;
            const maxHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = (scrolled / maxHeight) * 100;
            
            const indicator = document.querySelector('.scroll-indicator');
            if (indicator) {{
                indicator.style.width = progress + '%';
            }}
        }});
        
        // Add scroll indicator on load
        document.addEventListener('DOMContentLoaded', () => {{
            const indicator = document.createElement('div');
            indicator.className = 'scroll-indicator';
            document.body.appendChild(indicator);
        }});
    </script>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <div class="glass-card header">
            <h1><i class="fas fa-cricket-bat-ball"></i> Cricket Performance Analytics</h1>
            <div class="player-profile">
                <div class="player-avatar">
                    <img src="{self.player_pic_url}" alt="{self.player_name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                    <div class="avatar-fallback" style="display:none;">{self.player_name[0] if self.player_name else 'P'}</div>
                </div>
                <h2 class="player-name">{self.player_name}</h2>
            </div>
            <p class="timestamp"><i class="far fa-clock"></i> Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <div class="summary-grid">
            <div class="glass-card metric-card">
                <div class="metric-icon"><i class="fas fa-gamepad"></i></div>
                <div class="metric-label">Total Matches</div>
                <div class="metric-value">{all_summary['total_matches']}</div>
                <div class="metric-subtitle">Completed Games</div>
            </div>
            <div class="glass-card metric-card">
                <div class="metric-icon"><i class="fas fa-trophy"></i></div>
                <div class="metric-label">Victories</div>
                <div class="metric-value">{all_summary['total_wins']}</div>
                <div class="metric-subtitle">Successful Matches</div>
            </div>
            <div class="glass-card metric-card">
                <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{all_summary['win_percentage']:.1f}%</div>
                <div class="metric-subtitle">Success Percentage</div>
            </div>
            <div class="glass-card metric-card">
                <div class="metric-icon"><i class="fas fa-users"></i></div>
                <div class="metric-label">Opponents</div>
                <div class="metric-value">{all_summary['opponents_count']}</div>
                <div class="metric-subtitle">Unique Players</div>
            </div>
        </div>

        <div class="navigation">
            <button class="nav-tab active" onclick="showSection('all-tournaments')">
                <i class="fas fa-chart-bar"></i> All Tournaments
            </button>
            <button class="nav-tab" onclick="showSection('ibc-pro-360')">
                <i class="fas fa-star"></i> iBC PRO 360
            </button>
            <button class="nav-tab" onclick="showSection('ibc-360')">
                <i class="fas fa-target"></i> iBC 360
            </button>
        </div>

        <div id="all-tournaments" class="content-section active">
            <div class="glass-card tournament-content">
                <h2 class="section-title">
                    <i class="fas fa-chart-bar"></i>
                    Complete Performance Overview
                </h2>
                {self._generate_premium_html_table("All")}
            </div>
        </div>

        <div id="ibc-pro-360" class="content-section">
            <div class="glass-card tournament-content">
                <h2 class="section-title">
                    <i class="fas fa-star"></i>
                    iBC PRO 360 Tournament Analysis
                </h2>
                <div class="summary-grid" style="margin-bottom: 30px;">
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-gamepad"></i></div>
                        <div class="metric-label">Matches</div>
                        <div class="metric-value">{pro_summary['total_matches']}</div>
                    </div>
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-trophy"></i></div>
                        <div class="metric-label">Wins</div>
                        <div class="metric-value">{pro_summary['total_wins']}</div>
                    </div>
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value">{pro_summary['win_percentage']:.1f}%</div>
                    </div>
                </div>
                {self._generate_premium_html_table("iBC PRO 360")}
            </div>
        </div>

        <div id="ibc-360" class="content-section">
            <div class="glass-card tournament-content">
                <h2 class="section-title">
                    <i class="fas fa-target"></i>
                    iBC 360 Tournament Analysis
                </h2>
                <div class="summary-grid" style="margin-bottom: 30px;">
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-gamepad"></i></div>
                        <div class="metric-label">Matches</div>
                        <div class="metric-value">{bc_summary['total_matches']}</div>
                    </div>
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-trophy"></i></div>
                        <div class="metric-label">Wins</div>
                        <div class="metric-value">{bc_summary['total_wins']}</div>
                    </div>
                    <div class="glass-card metric-card">
                        <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value">{bc_summary['win_percentage']:.1f}%</div>
                    </div>
                </div>
                {self._generate_premium_html_table("iBC 360")}
            </div>
        </div>

    </div>
</body>
</html>
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Premium HTML report generated: {filename}")
        return filename

    def _generate_premium_html_table(self, tournament_filter="All"):
        """Generate premium HTML table with sophisticated design"""
        if tournament_filter == "All":
            stats_data = self.head_to_head_stats
        else:
            stats_data = self.tournament_stats.get(tournament_filter, {})

        if not stats_data:
            return '''
            <div class="empty-state">
                <i class="fas fa-search" style="font-size: 3rem; color: #475569; margin-bottom: 16px;"></i>
                <h3>No Match Data Available</h3>
                <p>No matches found for this tournament category.</p>
            </div>
            '''

        # Sort opponents by total matches (descending)
        sorted_opponents = sorted(
            stats_data.items(),
            key=lambda x: x[1]['total_matches'],
            reverse=True
        )

        table_html = '''
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-users"></i> Matchup</th>
                        <th><i class="fas fa-user"></i> Opponent</th>
                        <th><i class="fas fa-gamepad"></i> Total</th>
                        <th><i class="fas fa-trophy"></i> Wins</th>
                        <th><i class="fas fa-times-circle"></i> Losses</th>
                        <th><i class="fas fa-chart-line"></i> Win Rate</th>
                    </tr>
                </thead>
                <tbody>
        '''

        for opponent, stats in sorted_opponents:
            wins = stats['wins']
            losses = stats['losses']
            total = stats['total_matches']
            win_percentage = (wins / total * 100) if total > 0 else 0

            # Color coding for win rate
            if win_percentage >= 70:
                rate_class = "win-rate-high"
            elif win_percentage >= 40:
                rate_class = "win-rate-medium"
            else:
                rate_class = "win-rate-low"

            # Get opponent picture
            opponent_pic = self.opponent_pics.get(opponent, '')
            opponent_initial = opponent[0] if opponent else 'U'

            table_html += f'''
                <tr>
                    <td>
                        <div class="player-matchup">
                            <div class="avatar-container">
                                <img src="{self.player_pic_url}" alt="{self.player_name}" class="avatar" 
                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                                <div class="avatar-fallback" style="display:none;">{self.player_name[0] if self.player_name else 'P'}</div>
                            </div>
                            <span class="vs-indicator">VS</span>
                            <div class="avatar-container">
                                <img src="{opponent_pic}" alt="{opponent}" class="avatar" 
                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                                <div class="avatar-fallback" style="display:none;">{opponent_initial}</div>
                            </div>
                        </div>
                    </td>
                    <td class="opponent-name">{opponent}</td>
                    <td class="stat-number total">{total}</td>
                    <td class="stat-number wins">{wins}</td>
                    <td class="stat-number losses">{losses}</td>
                    <td>
                        <span class="win-rate-badge {rate_class}">{win_percentage:.1f}%</span>
                    </td>
                </tr>
            '''

        table_html += '''
                </tbody>
            </table>
        </div>
        '''
        return table_html

    def get_tournament_subtypes(self, main_type):
        """Get all subtypes for a tournament type"""
        subtypes = []
        for tournament_type in self.tournament_stats.keys():
            if tournament_type.startswith(main_type) and " - " in tournament_type:
                subtypes.append(tournament_type)
        return sorted(subtypes)


def main():
    """Main function"""
    print("🏏 Enhanced Cricket Head-to-Head Report Generator")
    print("=" * 60)

    # Initialize
    generator = CricketReportGenerator()

    # Load data
    print("\n📂 Loading tournament data...")
    data_files = ["data/tournament1.json", "data/tournament2.json"]
    generator.load_data(data_files)

    if not generator.data:
        print("❌ No data loaded! Please check your data files.")
        return

    print(f"\n✅ Total matches loaded: {len(generator.data)}")

    # Calculate statistics
    generator.calculate_statistics()

    # Print summaries
    all_summary = generator.print_tournament_summary("All")
    pro_summary = generator.print_tournament_summary("iBC PRO 360")
    bc_summary = generator.print_tournament_summary("iBC 360")

    # Show subtypes
    print(f"\n📋 TOURNAMENT SUBTYPES ANALYSIS")
    print("="*60)

    pro_subtypes = generator.get_tournament_subtypes("iBC PRO 360")
    print(f"\n🏆 iBC PRO 360 Subtypes ({len(pro_subtypes)}):")
    for subtype in pro_subtypes:
        subtype_summary = generator.get_statistics_summary(subtype)
        if subtype_summary['total_matches'] > 0:
            print(
                f"   {subtype}: {subtype_summary['total_matches']} matches, {subtype_summary['win_percentage']:.1f}% win rate")

    bc_subtypes = generator.get_tournament_subtypes("iBC 360")
    print(f"\n🎯 iBC 360 Subtypes ({len(bc_subtypes)}):")
    for subtype in bc_subtypes:
        subtype_summary = generator.get_statistics_summary(subtype)
        if subtype_summary['total_matches'] > 0:
            print(
                f"   {subtype}: {subtype_summary['total_matches']} matches, {subtype_summary['win_percentage']:.1f}% win rate")

    # Generate reports
    print(f"\n📝 GENERATING REPORTS")
    print("="*40)

    detailed_report = generator.generate_detailed_report()
    csv_export = generator.generate_csv_export()
    html_report = generator.generate_html_report()

    # Final summary
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"📊 Tournament types found: {list(generator.tournament_types)}")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Files created:")
    print(f"   📄 Detailed Report: {detailed_report}")
    print(f"   📊 CSV Export: {csv_export}")
    print(f"   🌐 HTML Report: {html_report}")

    print(f"\n📈 FINAL SUMMARY:")
    print(f"   Total Opponents: {all_summary['opponents_count']}")
    print(f"   Overall Win Rate: {all_summary['win_percentage']:.1f}%")
    print(f"   iBC PRO 360 Win Rate: {pro_summary['win_percentage']:.1f}%")
    print(f"   iBC 360 Win Rate: {bc_summary['win_percentage']:.1f}%")


if __name__ == "__main__":
    main()
