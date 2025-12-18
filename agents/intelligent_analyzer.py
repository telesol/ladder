#!/usr/bin/env python3
"""
Intelligent Analyzer - Comprehensive exploration of existing data and history
Builds complete understanding before autonomous reasoning begins
"""
import os
import sys
import json
import csv
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class IntelligentAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis_report = {}
        self.discovered_patterns = []
        self.knowledge_insights = []
        self.mission_understanding = {}
        
    async def analyze_system(self) -> Dict[str, Any]:
        """Perform system analysis - alias for comprehensive_analysis"""
        return await self.comprehensive_analysis()
        
    async def comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform complete analysis of all available data and documentation"""
        pass  # Silent
        pass  # Silent
        
        # Analyze all data sources systematically
        self._analyze_csv_data()
        self._analyze_databases()
        self._analyze_documentation()
        self._analyze_code_history()
        self._analyze_progress_files()
        self._analyze_mission_statements()
        self._identify_mathematical_patterns()
        self._assess_current_state()
        
        # Generate comprehensive report
        report = self._generate_intelligence_report()
        
        pass  # Silent
        return report
    
    def _analyze_csv_data(self):
        """Analyze Bitcoin puzzle CSV data"""
        pass  # Silent
        
        csv_files = list(self.base_path.glob("**/*.csv"))
        csv_insights = []
        
        # Limit to relevant CSV files to prevent overwhelming the system
        relevant_files = []
        for csv_file in csv_files:
            # Skip system files and only include project-relevant files
            if any(skip in str(csv_file) for skip in ['.venv', '__pycache__', 'site-packages']):
                continue
            relevant_files.append(csv_file)
        
        # Further limit to prevent token overflow - max 10 relevant files
        relevant_files = relevant_files[:10]
        
        for csv_file in relevant_files:
            try:
                pass  # Silent
                
                # Read CSV with pandas for better analysis
                df = pd.read_csv(csv_file)
                
                insights = {
                    'file': str(csv_file),
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'data_types': df.dtypes.to_dict(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'numeric_summary': self._get_numeric_summary(df),
                    'sample_data': df.head(3).to_dict('records'),  # Reduced from 5 to 3
                    'unique_values': {col: df[col].nunique() for col in df.columns}
                }
                
                # Look for mathematical patterns
                if 'puzzle' in str(csv_file).lower():
                    puzzle_insights = self._analyze_puzzle_data(df)
                    insights['puzzle_analysis'] = puzzle_insights
                
                csv_insights.append(insights)
                
            except Exception as e:
                print(f"  ⚠️  Error processing {csv_file}: {e}")
        
        self.analysis_report['csv_data'] = csv_insights
    
    def _analyze_puzzle_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Specialized analysis for puzzle data"""
        insights = {}
        
        # Look for common puzzle-related columns
        puzzle_cols = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['puzzle', 'address', 'key', 'private', 'public', 'solution'])]
        
        if puzzle_cols:
            insights['puzzle_columns'] = puzzle_cols
            
            # Analyze numeric patterns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                insights['numeric_patterns'] = {}
                for col in numeric_cols:
                    insights['numeric_patterns'][col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'unique_count': int(df[col].nunique()),
                        'distribution_type': self._analyze_distribution(df[col])
                    }
        
        return insights
    
    def _analyze_distribution(self, series: pd.Series) -> str:
        """Analyze distribution type of numeric data"""
        from scipy import stats
        import numpy as np
        
        try:
            # Remove NaN values
            clean_data = series.dropna()
            
            if len(clean_data) < 10:
                return "insufficient_data"
            
            # Test for uniform distribution
            _, p_uniform = stats.kstest(clean_data, 'uniform', 
                                       args=(clean_data.min(), clean_data.max() - clean_data.min()))
            
            # Test for normal distribution
            _, p_normal = stats.shapiro(clean_data[:min(5000, len(clean_data))])  # Shapiro has limit
            
            # Test for exponential distribution
            _, p_exponential = stats.kstest(clean_data, 'expon', 
                                            args=(clean_data.min(),))
            
            if p_uniform > 0.05:
                return "uniform"
            elif p_normal > 0.05:
                return "normal"
            elif p_exponential > 0.05:
                return "exponential"
            else:
                return "unknown"
                
        except Exception:
            return "analysis_failed"
    
    def _analyze_databases(self):
        """Analyze SQLite databases"""
        pass  # Silent
        
        db_files = list(self.base_path.glob("**/*.db")) + list(self.base_path.glob("**/*.sqlite"))
        db_insights = []
        
        for db_file in db_files:
            try:
                pass  # Silent
                
                conn = sqlite3.connect(db_file)
                
                # Get table information
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                db_info = {
                    'file': str(db_file),
                    'tables': []
                }
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    # Get sample data
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    sample_data = cursor.fetchall()
                    
                    table_info = {
                        'name': table_name,
                        'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                        'row_count': row_count,
                        'sample_data': sample_data
                    }
                    
                    # Analyze content if it's puzzle-related
                    if any(keyword in table_name.lower() for keyword in ['puzzle', 'solution', 'key', 'address']):
                        table_info['content_analysis'] = self._analyze_table_content(conn, table_name)
                    
                    db_info['tables'].append(table_info)
                
                db_insights.append(db_info)
                conn.close()
                
            except Exception as e:
                print(f"  ⚠️  Error processing {db_file}: {e}")
        
        self.analysis_report['databases'] = db_insights
    
    def _analyze_table_content(self, conn: sqlite3.Connection, table_name: str) -> Dict[str, Any]:
        """Analyze content of puzzle-related tables"""
        cursor = conn.cursor()
        
        analysis = {}
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Look for numeric columns
        numeric_cols = []
        for col in columns:
            cursor.execute(f"SELECT typeof({col}) FROM {table_name} WHERE {col} IS NOT NULL LIMIT 1")
            result = cursor.fetchone()
            if result and result[0] in ('integer', 'real'):
                numeric_cols.append(col)
        
        if numeric_cols:
            analysis['numeric_columns'] = {}
            for col in numeric_cols:
                cursor.execute(f"SELECT MIN({col}), MAX({col}), AVG({col}), COUNT(DISTINCT {col}) FROM {table_name}")
                stats = cursor.fetchone()
                analysis['numeric_columns'][col] = {
                    'min': stats[0],
                    'max': stats[1],
                    'avg': stats[2],
                    'unique_count': stats[3]
                }
        
        return analysis
    
    def _analyze_documentation(self):
        """Analyze documentation files"""
        pass  # Silent
        
        doc_files = list(self.base_path.glob("**/*.md")) + list(self.base_path.glob("**/*.txt"))
        doc_insights = []
        
        # Filter out system files and limit to project-relevant documentation
        relevant_files = []
        for doc_file in doc_files:
            # Skip system files and only include project-relevant files
            if any(skip in str(doc_file) for skip in ['.venv', '__pycache__', 'site-packages']):
                continue
            relevant_files.append(doc_file)
        
        # Further limit to prevent token overflow - max 15 relevant files
        relevant_files = relevant_files[:15]
        
        for doc_file in relevant_files:
            try:
                pass  # Silent
                
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract key information - limit content size
                max_content_size = 50000  # 50KB max per file
                if len(content) > max_content_size:
                    content = content[:max_content_size] + "... [truncated]"
                
                insights = {
                    'file': str(doc_file),
                    'size': len(content),
                    'lines': len(content.split('\n')),
                    'key_topics': self._extract_key_topics(content),
                    'mathematical_content': self._extract_mathematical_content(content),
                    'progress_indicators': self._extract_progress_info(content),
                    'mentioned_files': self._extract_mentioned_files(content)
                }
                
                doc_insights.append(insights)
                
            except Exception as e:
                print(f"  ⚠️  Error processing {doc_file}: {e}")
        
        self.analysis_report['documentation'] = doc_insights
    
    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from documentation"""
        topics = []
        
        # Look for headers (markdown)
        import re
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        topics.extend(headers)
        
        # Look for key terms
        key_terms = [
            'puzzle', 'bitcoin', 'affine', 'recurrence', 'solution', 
            'algorithm', 'pattern', 'key', 'private', 'public', 'address',
            'ladder', 'modulo', 'cryptography', 'mathematical', 'proof'
        ]
        
        content_lower = content.lower()
        for term in key_terms:
            if term in content_lower:
                # Count occurrences to gauge importance
                count = content_lower.count(term)
                if count > 2:
                    topics.append(f"{term} ({count} mentions)")
        
        return topics[:10]  # Top 10 topics
    
    def _extract_mathematical_content(self, content: str) -> Dict[str, Any]:
        """Extract mathematical equations and concepts"""
        math_content = {
            'equations': [],
            'variables': [],
            'concepts': []
        }
        
        import re
        
        # Look for equations (simple pattern)
        equations = re.findall(r'[a-zA-Z]\s*=\s*[^=\n]+', content)
        math_content['equations'] = equations[:5]  # First 5 equations
        
        # Look for mathematical variables (single letters or Greek letters)
        variables = re.findall(r'\b[a-zA-Z]\b', content)
        var_counts = {}
        for var in variables:
            if len(var) == 1 and var.isalpha():
                var_counts[var] = var_counts.get(var, 0) + 1
        
        # Get most common variables (likely mathematical)
        sorted_vars = sorted(var_counts.items(), key=lambda x: x[1], reverse=True)
        math_content['variables'] = [f"{var} ({count})" for var, count in sorted_vars[:10]]
        
        # Look for mathematical concepts
        concepts = ['modulo', 'affine', 'recurrence', 'linear', 'equation', 'algorithm', 'proof']
        content_lower = content.lower()
        for concept in concepts:
            if concept in content_lower:
                math_content['concepts'].append(concept)
        
        return math_content
    
    def _extract_progress_info(self, content: str) -> Dict[str, Any]:
        """Extract progress and status information"""
        progress_info = {
            'mentioned_puzzles': [],
            'completion_status': [],
            'challenges': [],
            'breakthroughs': []
        }
        
        import re
        
        # Look for puzzle numbers
        puzzles = re.findall(r'puzzle\s*#?(\d+)', content, re.IGNORECASE)
        progress_info['mentioned_puzzles'] = list(set(puzzles))
        
        # Look for completion indicators
        completion_patterns = [
            r'solved', r'completed', r'finished', r'done', r'success',
            r'working', r'in progress', r'partial', r'failed', r'stuck'
        ]
        
        content_lower = content.lower()
        for pattern in completion_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                progress_info['completion_status'].append(f"{pattern} ({len(matches)})")
        
        return progress_info
    
    def _extract_mentioned_files(self, content: str) -> List[str]:
        """Extract mentioned files and paths"""
        import re
        
        # Look for file references
        files = re.findall(r'\b[\w\-]+\.(csv|json|py|md|txt|db|sqlite)\b', content)
        return list(set(files))
    
    def _analyze_code_history(self):
        """Analyze Python code files for mathematical approaches"""
        pass  # Silent
        
        py_files = list(self.base_path.glob("**/*.py"))
        code_insights = []
        
        # Filter out system files and limit to project-relevant files
        relevant_files = []
        for py_file in py_files:
            # Skip system files and only include project-relevant files
            if any(skip in str(py_file) for skip in ['.venv', '__pycache__', 'site-packages']):
                continue
            relevant_files.append(py_file)
        
        # Further limit to prevent token overflow - max 20 relevant files
        relevant_files = relevant_files[:20]
        
        for py_file in relevant_files:
            try:
                pass  # Silent
                
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Limit content size to prevent memory issues
                max_content_size = 100000  # 100KB max per file
                if len(content) > max_content_size:
                    content = content[:max_content_size] + "... [truncated]"
                
                insights = {
                    'file': str(py_file),
                    'functions': self._extract_functions(content),
                    'mathematical_operations': self._extract_math_operations(content),
                    'imported_modules': self._extract_imports(content),
                    'key_variables': self._extract_key_variables(content),
                    'algorithmic_approaches': self._extract_algorithmic_approaches(content)
                }
                
                code_insights.append(insights)
                
            except Exception as e:
                print(f"  ⚠️  Error processing {py_file}: {e}")
        
        self.analysis_report['code_history'] = code_insights
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions and their purposes"""
        import re
        
        functions = []
        func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
        
        matches = re.finditer(func_pattern, content)
        for match in matches:
            func_name = match.group(1)
            start = match.start()
            
            # Get function docstring if present
            docstring_match = re.search(r'"""([^"]*)"""', content[start:start+500])
            docstring = docstring_match.group(1) if docstring_match else ""
            
            functions.append({
                'name': func_name,
                'docstring': docstring[:100],  # First 100 chars
                'purpose': self._infer_function_purpose(func_name, docstring)
            })
        
        return functions[:10]  # Top 10 functions
    
    def _infer_function_purpose(self, func_name: str, docstring: str) -> str:
        """Infer function purpose from name and docstring"""
        name_lower = func_name.lower()
        doc_lower = docstring.lower()
        
        if any(word in name_lower for word in ['solve', 'find', 'calculate', 'compute']):
            return "computation"
        elif any(word in name_lower for word in ['verify', 'check', 'validate']):
            return "verification"
        elif any(word in name_lower for word in ['generate', 'create', 'make']):
            return "generation"
        elif any(word in name_lower for word in ['analyze', 'extract', 'parse']):
            return "analysis"
        else:
            return "utility"
    
    def _extract_math_operations(self, content: str) -> List[str]:
        """Extract mathematical operations"""
        import re
        
        operations = []
        
        # Look for mathematical operators
        math_patterns = [
            r'\*\*',  # Power
            r'\bmod\b',  # Modulo
            r'%',  # Modulo operator
            r'//',  # Floor division
            r'math\.',  # Math module functions
            r'numpy\.',  # NumPy functions
            r'scipy\.',  # SciPy functions
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, content)
            if matches:
                operations.extend(matches)
        
        return list(set(operations))
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract imported modules"""
        import re
        
        imports = re.findall(r'^(?:import|from)\s+(\w+)', content, re.MULTILINE)
        return list(set(imports))
    
    def _extract_key_variables(self, content: str) -> List[str]:
        """Extract key variable names"""
        import re
        
        # Look for variable assignments
        var_assignments = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
        
        # Count frequency
        var_counts = {}
        for var in var_assignments:
            if len(var) > 2:  # Filter out single letters
                var_counts[var] = var_counts.get(var, 0) + 1
        
        # Get most common
        sorted_vars = sorted(var_counts.items(), key=lambda x: x[1], reverse=True)
        return [var for var, count in sorted_vars[:10]]
    
    def _extract_algorithmic_approaches(self, content: str) -> List[str]:
        """Extract algorithmic approaches"""
        approaches = []
        
        content_lower = content.lower()
        
        algorithm_keywords = [
            'brute force', 'recursive', 'iterative', 'dynamic programming',
            'greedy', 'backtracking', 'divide and conquer', 'binary search',
            'sorting', 'hashing', 'tree', 'graph', 'matrix'
        ]
        
        for keyword in algorithm_keywords:
            if keyword in content_lower:
                approaches.append(keyword)
        
        return approaches
    
    def _analyze_progress_files(self):
        """Analyze progress tracking files"""
        pass  # Silent
        
        progress_keywords = ['progress', 'todo', 'status', 'log']
        progress_files = []
        
        for keyword in progress_keywords:
            progress_files.extend(self.base_path.glob(f"**/*{keyword}*"))
        
        progress_insights = []
        
        for file in progress_files:
            if file.is_file():
                try:
                    pass  # Silent
                    
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    insights = {
                        'file': str(file),
                        'progress_indicators': self._extract_progress_markers(content),
                        'timeline': self._extract_timeline(content),
                        'milestones': self._extract_milestones(content),
                        'blockers': self._extract_blockers(content)
                    }
                    
                    progress_insights.append(insights)
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing {file}: {e}")
        
        self.analysis_report['progress_tracking'] = progress_insights
    
    def _extract_progress_markers(self, content: str) -> List[str]:
        """Extract progress markers"""
        import re
        
        markers = []
        
        # Look for completion markers
        completion_patterns = [
            r'✓\s*(.+)', r'\[x\]\s*(.+)', r'DONE:\s*(.+)', 
            r'COMPLETED:\s*(.+)', r'SOLVED:\s*(.+)'
        ]
        
        for pattern in completion_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            markers.extend(matches)
        
        return markers[:10]
    
    def _extract_timeline(self, content: str) -> List[str]:
        """Extract timeline information"""
        import re
        
        # Look for dates
        dates = re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}', content)
        return dates[:5]
    
    def _extract_milestones(self, content: str) -> List[str]:
        """Extract milestones"""
        import re
        
        milestone_patterns = [
            r'milestone:\s*(.+)', r'achievement:\s*(.+)', 
            r'breakthrough:\s*(.+)', r'key finding:\s*(.+)'
        ]
        
        milestones = []
        for pattern in milestone_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            milestones.extend(matches)
        
        return milestones[:5]
    
    def _extract_blockers(self, content: str) -> List[str]:
        """Extract blockers and challenges"""
        import re
        
        blocker_patterns = [
            r'blocker:\s*(.+)', r'issue:\s*(.+)', r'problem:\s*(.+)',
            r'challenge:\s*(.+)', r'stuck:\s*(.+)', r'failed:\s*(.+)'
        ]
        
        blockers = []
        for pattern in blocker_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            blockers.extend(matches)
        
        return blockers[:5]
    
    def _analyze_mission_statements(self):
        """Analyze mission and goal statements"""
        pass  # Silent
        
        mission_files = list(self.base_path.glob("**/mission*")) + list(self.base_path.glob("**/goal*"))
        mission_insights = []
        
        for file in mission_files:
            if file.is_file():
                try:
                    pass  # Silent
                    
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    insights = {
                        'file': str(file),
                        'primary_goals': self._extract_goals(content),
                        'target_metrics': self._extract_metrics(content),
                        'success_criteria': self._extract_success_criteria(content),
                        'constraints': self._extract_constraints(content)
                    }
                    
                    mission_insights.append(insights)
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing {file}: {e}")
        
        self.analysis_report['mission_analysis'] = mission_insights
    
    def _extract_goals(self, content: str) -> List[str]:
        """Extract primary goals"""
        import re
        
        goal_patterns = [
            r'goal:\s*(.+)', r'objective:\s*(.+)', r'aim:\s*(.+)',
            r'purpose:\s*(.+)', r'mission:\s*(.+)'
        ]
        
        goals = []
        for pattern in goal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            goals.extend(matches)
        
        return goals[:5]
    
    def _extract_metrics(self, content: str) -> List[str]:
        """Extract target metrics"""
        import re
        
        # Look for numbers and percentages
        metrics = re.findall(r'\d+%?|\d+\.\d+%?', content)
        return list(set(metrics))[:10]
    
    def _extract_success_criteria(self, content: str) -> List[str]:
        """Extract success criteria"""
        import re
        
        success_patterns = [
            r'success:\s*(.+)', r'criteria:\s*(.+)', r'requirement:\s*(.+)',
            r'validation:\s*(.+)', r'verification:\s*(.+)'
        ]
        
        criteria = []
        for pattern in success_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            criteria.extend(matches)
        
        return criteria[:5]
    
    def _extract_constraints(self, content: str) -> List[str]:
        """Extract constraints and limitations"""
        import re
        
        constraint_patterns = [
            r'constraint:\s*(.+)', r'limitation:\s*(.+)', r'restriction:\s*(.+)',
            r'cannot:\s*(.+)', r'must not:\s*(.+)'
        ]
        
        constraints = []
        for pattern in constraint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            constraints.extend(matches)
        
        return constraints[:5]
    
    def _identify_mathematical_patterns(self):
        """Identify mathematical patterns across all data"""
        pass  # Silent
        
        patterns = []
        
        # Analyze numeric relationships in CSV data
        if 'csv_data' in self.analysis_report:
            for csv_info in self.analysis_report['csv_data']:
                if 'puzzle_analysis' in csv_info:
                    patterns.extend(self._extract_patterns_from_puzzle_data(csv_info))
        
        # Analyze mathematical operations in code
        if 'code_history' in self.analysis_report:
            for code_info in self.analysis_report['code_history']:
                patterns.extend(self._extract_patterns_from_code(code_info))
        
        # Analyze patterns in databases
        if 'databases' in self.analysis_report:
            for db_info in self.analysis_report['databases']:
                patterns.extend(self._extract_patterns_from_database(db_info))
        
        self.discovered_patterns = patterns
    
    def _extract_patterns_from_puzzle_data(self, csv_info: Dict) -> List[Dict[str, Any]]:
        """Extract patterns from puzzle data"""
        patterns = []
        
        if 'numeric_patterns' in csv_info.get('puzzle_analysis', {}):
            for col, stats in csv_info['puzzle_analysis']['numeric_patterns'].items():
                pattern = {
                    'type': 'numeric_distribution',
                    'source': csv_info['file'],
                    'column': col,
                    'pattern_details': stats,
                    'significance': self._assess_pattern_significance(stats)
                }
                patterns.append(pattern)
        
        return patterns
    
    def _extract_patterns_from_code(self, code_info: Dict) -> List[Dict[str, Any]]:
        """Extract patterns from code analysis"""
        patterns = []
        
        # Look for mathematical operations
        if 'mathematical_operations' in code_info:
            for op in code_info['mathematical_operations']:
                pattern = {
                    'type': 'mathematical_operation',
                    'source': code_info['file'],
                    'operation': op,
                    'significance': 'operational'
                }
                patterns.append(pattern)
        
        # Look for algorithmic approaches
        if 'algorithmic_approaches' in code_info:
            for approach in code_info['algorithmic_approaches']:
                pattern = {
                    'type': 'algorithmic_approach',
                    'source': code_info['file'],
                    'approach': approach,
                    'significance': 'strategic'
                }
                patterns.append(pattern)
        
        return patterns
    
    def _extract_patterns_from_database(self, db_info: Dict) -> List[Dict[str, Any]]:
        """Extract patterns from database analysis"""
        patterns = []
        
        for table in db_info.get('tables', []):
            if 'content_analysis' in table:
                analysis = table['content_analysis']
                if 'numeric_columns' in analysis:
                    for col, stats in analysis['numeric_columns'].items():
                        pattern = {
                            'type': 'database_numeric_pattern',
                            'source': f"{db_info['file']}::{table['name']}",
                            'column': col,
                            'pattern_details': stats,
                            'significance': self._assess_pattern_significance(stats)
                        }
                        patterns.append(pattern)
        
        return patterns
    
    def _assess_pattern_significance(self, stats: Dict) -> str:
        """Assess the significance of a discovered pattern"""
        # Simple heuristic for pattern significance
        if 'unique_count' in stats and 'row_count' in stats:
            if stats['unique_count'] == stats['row_count']:
                return "high"  # All unique values
            elif stats['unique_count'] / stats['row_count'] < 0.1:
                return "high"  # Low cardinality
            else:
                return "medium"
        
        if 'min' in stats and 'max' in stats:
            range_size = stats['max'] - stats['min']
            if range_size > 0 and range_size < 1000:
                return "medium"
            else:
                return "low"
        
        return "unknown"
    
    def _assess_current_state(self):
        """Assess the current state of the project"""
        pass  # Silent
        
        assessment = {
            'data_completeness': self._assess_data_completeness(),
            'mathematical_readiness': self._assess_mathematical_readiness(),
            'historical_progress': self._assess_historical_progress(),
            'available_approaches': self._assess_available_approaches(),
            'knowledge_gaps': self._identify_knowledge_gaps(),
            'success_likelihood': self._assess_success_likelihood()
        }
        
        self.mission_understanding = assessment
    
    def _assess_data_completeness(self) -> Dict[str, Any]:
        """Assess completeness of available data"""
        completeness = {
            'puzzle_data_available': False,
            'solution_data_available': False,
            'historical_attempts_available': False,
            'mathematical_models_available': False,
            'verification_data_available': False
        }
        
        # Check for puzzle data
        if 'csv_data' in self.analysis_report:
            for csv_info in self.analysis_report['csv_data']:
                if 'puzzle_analysis' in csv_info:
                    completeness['puzzle_data_available'] = True
                    break
        
        # Check for solution data
        if 'databases' in self.analysis_report:
            for db_info in self.analysis_report['databases']:
                for table in db_info.get('tables', []):
                    if 'solution' in table['name'].lower():
                        completeness['solution_data_available'] = True
                        break
        
        # Check for historical attempts
        if 'progress_tracking' in self.analysis_report:
            completeness['historical_attempts_available'] = len(self.analysis_report['progress_tracking']) > 0
        
        # Check for mathematical models
        if 'code_history' in self.analysis_report:
            for code_info in self.analysis_report['code_history']:
                if 'mathematical_operations' in code_info and code_info['mathematical_operations']:
                    completeness['mathematical_models_available'] = True
                    break
        
        return completeness
    
    def _assess_mathematical_readiness(self) -> Dict[str, Any]:
        """Assess mathematical readiness for autonomous solving"""
        readiness = {
            'affine_models_available': False,
            'modulo_arithmetic_available': False,
            'pattern_recognition_available': False,
            'verification_methods_available': False,
            'computational_tools_available': False
        }
        
        # Check for affine/linear models
        if 'discovered_patterns' in dir(self):
            for pattern in self.discovered_patterns:
                if 'affine' in str(pattern).lower() or 'linear' in str(pattern).lower():
                    readiness['affine_models_available'] = True
                    break
        
        # Check for modulo operations
        if 'code_history' in self.analysis_report:
            for code_info in self.analysis_report['code_history']:
                if 'mod' in code_info.get('mathematical_operations', []):
                    readiness['modulo_arithmetic_available'] = True
                    break
        
        # Check for pattern recognition
        if 'discovered_patterns' in dir(self) and len(self.discovered_patterns) > 0:
            readiness['pattern_recognition_available'] = True
        
        # Check for computational tools
        if 'code_history' in self.analysis_report:
            for code_info in self.analysis_report['code_history']:
                if any(mod in ['math', 'numpy', 'scipy'] for mod in code_info.get('imported_modules', [])):
                    readiness['computational_tools_available'] = True
                    break
        
        return readiness
    
    def _assess_historical_progress(self) -> Dict[str, Any]:
        """Assess historical progress made"""
        progress = {
            'puzzles_solved': 0,
            'puzzles_attempted': 0,
            'successful_approaches': [],
            'failed_approaches': [],
            'major_breakthroughs': [],
            'current_blockers': []
        }
        
        # Analyze progress files
        if 'progress_tracking' in self.analysis_report:
            for progress_info in self.analysis_report['progress_tracking']:
                if 'milestones' in progress_info:
                    progress['major_breakthroughs'].extend(progress_info['milestones'])
                
                if 'blockers' in progress_info:
                    progress['current_blockers'].extend(progress_info['blockers'])
        
        # Analyze documentation for solved puzzles
        if 'documentation' in self.analysis_report:
            for doc_info in self.analysis_report['documentation']:
                if 'progress_indicators' in doc_info:
                    for indicator in doc_info['progress_indicators']:
                        if 'solved' in indicator.lower() or 'completed' in indicator.lower():
                            progress['puzzles_solved'] += 1
        
        return progress
    
    def _assess_available_approaches(self) -> List[Dict[str, Any]]:
        """Assess available mathematical approaches"""
        approaches = []
        
        # Based on code analysis
        if 'code_history' in self.analysis_report:
            for code_info in self.analysis_report['code_history']:
                if 'algorithmic_approaches' in code_info:
                    for approach in code_info['algorithmic_approaches']:
                        approaches.append({
                            'type': 'algorithmic',
                            'approach': approach,
                            'source': code_info['file'],
                            'applicability': 'general'
                        })
                
                if 'mathematical_operations' in code_info:
                    for op in code_info['mathematical_operations']:
                        approaches.append({
                            'type': 'mathematical',
                            'approach': op,
                            'source': code_info['file'],
                            'applicability': 'computational'
                        })
        
        # Based on discovered patterns
        if 'discovered_patterns' in dir(self):
            for pattern in self.discovered_patterns:
                approaches.append({
                    'type': 'pattern_based',
                    'approach': pattern['type'],
                    'source': pattern['source'],
                    'applicability': 'specific',
                    'significance': pattern['significance']
                })
        
        return approaches
    
    def _identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Identify knowledge gaps that need to be filled"""
        gaps = []
        
        # Check data completeness gaps
        completeness = self._assess_data_completeness()
        for key, available in completeness.items():
            if not available:
                gaps.append({
                    'type': 'data_gap',
                    'description': key.replace('_', ' ').replace('available', 'missing'),
                    'priority': 'high',
                    'impact': 'foundational'
                })
        
        # Check mathematical readiness gaps
        readiness = self._assess_mathematical_readiness()
        for key, available in readiness.items():
            if not available:
                gaps.append({
                    'type': 'mathematical_gap',
                    'description': key.replace('_', ' ').replace('available', 'needed'),
                    'priority': 'medium',
                    'impact': 'methodological'
                })
        
        return gaps
    
    def _assess_success_likelihood(self) -> Dict[str, Any]:
        """Assess likelihood of successful autonomous solving"""
        completeness = self._assess_data_completeness()
        readiness = self._assess_mathematical_readiness()
        
        # Calculate scores
        data_score = sum(completeness.values()) / len(completeness)
        math_score = sum(readiness.values()) / len(readiness)
        
        overall_score = (data_score + math_score) / 2
        
        likelihood = {
            'overall_score': overall_score,
            'data_readiness': data_score,
            'mathematical_readiness': math_score,
            'recommendation': self._generate_recommendation(overall_score),
            'risk_factors': self._identify_risk_factors()
        }
        
        return likelihood
    
    def _generate_recommendation(self, score: float) -> str:
        """Generate recommendation based on readiness score"""
        if score >= 0.8:
            return "High likelihood of success - proceed with full autonomous implementation"
        elif score >= 0.6:
            return "Moderate likelihood - address key gaps before full deployment"
        elif score >= 0.4:
            return "Low likelihood - significant groundwork needed"
        else:
            return "Very low likelihood - extensive data and methodology development required"
    
    def _identify_risk_factors(self) -> List[str]:
        """Identify risk factors for autonomous solving"""
        risks = []
        
        completeness = self._assess_data_completeness()
        readiness = self._assess_mathematical_readiness()
        
        if not completeness['puzzle_data_available']:
            risks.append("Insufficient puzzle data for pattern recognition")
        
        if not completeness['solution_data_available']:
            risks.append("No verified solutions for validation training")
        
        if not readiness['affine_models_available']:
            risks.append("Missing affine transformation models")
        
        if not readiness['verification_methods_available']:
            risks.append("No verification methods for solution validation")
        
        if not readiness['computational_tools_available']:
            risks.append("Insufficient mathematical computation tools")
        
        return risks
    
    def _generate_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        pass  # Silent

        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(),
            'data_inventory': self._compile_data_inventory(),
            'mathematical_insights': self.discovered_patterns,
            'historical_progress': self.mission_understanding.get('historical_progress', {}),
            'available_approaches': self.mission_understanding.get('available_approaches', []),
            'knowledge_gaps': self.mission_understanding.get('knowledge_gaps', []),
            'success_likelihood': self.mission_understanding.get('success_likelihood', {}),
            'strategic_recommendations': self._generate_strategic_recommendations(),
            'next_steps': self._generate_next_steps()
        }

        # Store report in database instead of file
        try:
            from memory_system import get_memory_system
            memory = get_memory_system()
            report_id = memory.store_intelligence_report(report, report_type='analysis')
            pass  # Silent

            # Cleanup old reports to prevent database bloat (keep last 100)
            deleted = memory.cleanup_old_reports(keep_count=100)
            if deleted > 0:
                pass  # Silent
        except Exception as e:
            print(f"⚠️ Could not store report in database: {e}")
            # Fallback: still log that we generated the report
            print(f"📋 Intelligence report generated at {report['analysis_timestamp']}")

        return report
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary of analysis"""
        likelihood = self.mission_understanding.get('success_likelihood', {})
        score = likelihood.get('overall_score', 0)
        
        summary = f"""
        COMPREHENSIVE INTELLIGENCE ANALYSIS COMPLETE
        
        Project Readiness Assessment:
        - Overall Success Likelihood: {score:.1%}
        - Data Completeness: {likelihood.get('data_readiness', 0):.1%}
        - Mathematical Readiness: {likelihood.get('mathematical_readiness', 0):.1%}
        
        Key Findings:
        - Discovered {len(self.discovered_patterns)} mathematical patterns
        - Analyzed {len(self.analysis_report.get('csv_data', []))} data files
        - Reviewed {len(self.analysis_report.get('code_history', []))} code implementations
        - Identified {len(self.mission_understanding.get('knowledge_gaps', []))} critical knowledge gaps
        
        Recommendation: {likelihood.get('recommendation', 'Analysis incomplete')}
        """
        
        return summary.strip()
    
    def _compile_data_inventory(self) -> Dict[str, Any]:
        """Compile complete data inventory"""
        inventory = {
            'csv_files': len(self.analysis_report.get('csv_data', [])),
            'database_files': len(self.analysis_report.get('databases', [])),
            'documentation_files': len(self.analysis_report.get('documentation', [])),
            'code_files': len(self.analysis_report.get('code_history', [])),
            'progress_files': len(self.analysis_report.get('progress_tracking', [])),
            'mission_files': len(self.analysis_report.get('mission_analysis', [])),
            'total_data_points': self._count_total_data_points(),
            'data_quality_score': self._assess_data_quality()
        }
        
        return inventory
    
    def _count_total_data_points(self) -> int:
        """Count total data points across all sources"""
        total_points = 0
        
        # Count CSV data points
        for csv_info in self.analysis_report.get('csv_data', []):
            if 'shape' in csv_info:
                total_points += csv_info['shape'][0] * csv_info['shape'][1]
        
        # Count database records
        for db_info in self.analysis_report.get('databases', []):
            for table in db_info.get('tables', []):
                total_points += table.get('row_count', 0)
        
        return total_points
    
    def _assess_data_quality(self) -> float:
        """Assess overall data quality"""
        # Simple quality score based on completeness and consistency
        quality_factors = []
        
        # Check for missing values in CSV files
        for csv_info in self.analysis_report.get('csv_data', []):
            if 'missing_values' in csv_info:
                total_missing = sum(csv_info['missing_values'].values())
                total_cells = csv_info['shape'][0] * csv_info['shape'][1]
                if total_cells > 0:
                    missing_ratio = total_missing / total_cells
                    quality_factors.append(1 - missing_ratio)
        
        # Check for database integrity
        for db_info in self.analysis_report.get('databases', []):
            for table in db_info.get('tables', []):
                if table.get('row_count', 0) > 0:
                    quality_factors.append(1.0)  # Assume good quality if data exists
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        gaps = self.mission_understanding.get('knowledge_gaps', [])
        for gap in gaps:
            if gap['priority'] == 'high':
                recommendations.append(f"Address critical gap: {gap['description']}")
        
        # Add strategic recommendations based on analysis
        if len(self.discovered_patterns) < 5:
            recommendations.append("Conduct deeper pattern analysis across all data sources")
        
        if not any('affine' in str(pattern).lower() for pattern in self.discovered_patterns):
            recommendations.append("Develop affine transformation models for puzzle solving")
        
        if not self.mission_understanding.get('historical_progress', {}).get('puzzles_solved', 0) > 0:
            recommendations.append("Establish baseline by solving simpler puzzles first")
        
        recommendations.append("Implement intelligent hypothesis generation based on discovered patterns")
        recommendations.append("Create robust verification system for mathematical solutions")
        
        return recommendations
    
    def _generate_next_steps(self) -> List[Dict[str, Any]]:
        """Generate specific next steps"""
        steps = [
            {
                'step': 1,
                'action': 'Address critical knowledge gaps identified in analysis',
                'priority': 'high',
                'estimated_effort': '1-2 days'
            },
            {
                'step': 2,
                'action': 'Implement intelligent pattern recognition system',
                'priority': 'high',
                'estimated_effort': '2-3 days'
            },
            {
                'step': 3,
                'action': 'Develop mathematical hypothesis generation engine',
                'priority': 'high',
                'estimated_effort': '3-4 days'
            },
            {
                'step': 4,
                'action': 'Create robust verification and validation system',
                'priority': 'medium',
                'estimated_effort': '2-3 days'
            },
            {
                'step': 5,
                'action': 'Implement adaptive learning and strategy refinement',
                'priority': 'medium',
                'estimated_effort': '3-5 days'
            },
            {
                'step': 6,
                'action': 'Deploy fully autonomous intelligent system',
                'priority': 'low',
                'estimated_effort': '1-2 days'
            }
        ]
        
        return steps
    
    def _get_numeric_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get numeric summary of dataframe"""
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        if numeric_df.empty:
            return {}
        
        summary = {
            'column_count': len(numeric_df.columns),
            'columns': list(numeric_df.columns),
            'correlations': numeric_df.corr().to_dict() if len(numeric_df.columns) > 1 else {}
        }
        
        return summary

def main():
    """Main function to run intelligent analysis"""
    print("🧠 Intelligent Analyzer for Bitcoin Puzzle System")
    pass  # Silent
    
    analyzer = IntelligentAnalyzer()
    report = analyzer.comprehensive_analysis()
    
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"📁 Files Analyzed: {len(report.get('data_inventory', {}))}")
    print(f"🔍 Patterns Discovered: {len(report.get('mathematical_insights', []))}")
    print(f"📈 Success Likelihood: {report.get('success_likelihood', {}).get('overall_score', 0):.1%}")
    print(f"⚠️  Knowledge Gaps: {len(report.get('knowledge_gaps', []))}")
    
    print("\n🎯 KEY RECOMMENDATIONS:")
    for rec in report.get('strategic_recommendations', [])[:3]:
        print(f"   • {rec}")
    
    print("\n⏭️  NEXT STEPS:")
    for step in report.get('next_steps', [])[:2]:
        print(f"   Step {step['step']}: {step['action']} ({step['estimated_effort']})")
    
    return report

if __name__ == "__main__":
    main()
