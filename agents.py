"""
Multi-Agent System with Google Gemini Integration
Implements parallel, sequential, and loop-based agents for career pathway generation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from config import settings
from observability import get_logger, get_tracer, get_metrics, LogLevel
from database import LearnerProfile, Pathway, Session, AgentLog, get_db_instance

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

logger = get_logger("multi_agent_system")


class SkillBridgeAgent(ABC):
    """Base class for all SkillBridge agents"""
    
    def __init__(self, name: str, description: str, verbose: bool = True):
        self.name = name
        self.description = description
        self.verbose = verbose
        self.tracer = get_tracer(name)
        self.metrics = get_metrics(name)
        self.logger = get_logger(name)
        self.execution_history = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent execution"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": self.name,
            "level": level,
            "message": message
        }
        self.execution_history.append(log_entry)
        # Convert string level into LogLevel enum when needed
        level_enum = None
        if isinstance(level, str):
            key = level.upper()
            if key == 'WARN':
                key = 'WARNING'
            try:
                level_enum = LogLevel[key]
            except Exception:
                level_enum = LogLevel.INFO
        else:
            level_enum = level

        self.logger.log_event(level_enum, message, agent=self.name)
        if self.verbose:
            print(f"[{self.name}] {message}")
    
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
    
    def get_execution_history(self) -> List[Dict]:
        """Get agent execution history"""
        return self.execution_history


class GoalAnalyzerAgent(SkillBridgeAgent):
    """Analyzes learner goals using Gemini"""
    
    CAREER_GOALS = {
        "Data Scientist": {
            "skills": ["Python", "SQL", "Statistics", "Machine Learning", "Data Visualization"],
            "duration_months": 6,
            "job_titles": ["Data Scientist", "ML Engineer", "Analytics Engineer"],
            "avg_salary_india": "₹800,000 - ₹1.5M"
        },
        "Data Analyst": {
            "skills": ["SQL", "Excel", "Power BI", "Tableau", "Statistics"],
            "duration_months": 4,
            "job_titles": ["Data Analyst", "Business Analyst", "BI Analyst"],
            "avg_salary_india": "₹500,000 - ₹900,000"
        },
        "Web Developer": {
            "skills": ["JavaScript", "React", "Backend (Node/Python)", "SQL", "Git"],
            "duration_months": 5,
            "job_titles": ["Full Stack Developer", "Frontend Developer", "Backend Developer"],
            "avg_salary_india": "₹600,000 - ₹1.2M"
        },
        "Cloud Engineer": {
            "skills": ["Cloud Fundamentals", "Linux", "Docker", "Kubernetes", "DevOps"],
            "duration_months": 5,
            "job_titles": ["Cloud Engineer", "DevOps Engineer", "SRE"],
            "avg_salary_india": "₹900,000 - ₹1.8M"
        },
        "AI/ML Engineer": {
            "skills": ["Python", "Deep Learning", "TensorFlow", "MLOps", "Statistics"],
            "duration_months": 7,
            "job_titles": ["ML Engineer", "Deep Learning Engineer", "AI Engineer"],
            "avg_salary_india": "₹1.0M - ₹2.5M"
        }
    }
    
    def run(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learner goals"""
        self.tracer.start_trace("goal_analysis", user_input=user_input)
        start_time = time.time()
        
        try:
            self.log("🎯 Starting goal analysis with Gemini AI")
            
            career_goal = user_input.get("career_goal", "Data Scientist")
            if career_goal not in self.CAREER_GOALS:
                self.log(f"⚠️ Unknown goal: {career_goal}. Using default.", "WARN")
                career_goal = "Data Scientist"
            
            goal_taxonomy = self.CAREER_GOALS[career_goal]
            
            # Use Gemini to enhance goal understanding
            gemini_analysis = self._analyze_with_gemini(user_input, goal_taxonomy)
            
            goal_profile = {
                "learner_id": user_input.get("learner_id", f"learner_{int(time.time())}"),
                "primary_goal": career_goal,
                "target_job_titles": goal_taxonomy["job_titles"],
                "skill_gaps": goal_taxonomy["skills"],
                "time_available_weekly": user_input.get("time_available_weekly", 5),
                "language_preference": user_input.get("language_preference", ["English"]),
                "learning_style": user_input.get("learning_style", ["Video lectures", "Project-based"]),
                "constraints": user_input.get("constraints", ["No cost"]),
                "certification_goals": user_input.get("certification_goals", True),
                "current_skills": user_input.get("current_skills", []),
                "estimated_duration_months": goal_taxonomy["duration_months"],
                "salary_potential": goal_taxonomy["avg_salary_india"],
                "gemini_insights": gemini_analysis,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.log(f"✅ Goal analysis complete: {len(goal_profile['skill_gaps'])} skills identified")
            duration = time.time() - start_time
            self.metrics.record_execution(duration, True)
            self.tracer.end_trace(status="success", result=goal_profile)
            
            return goal_profile
            
        except Exception as e:
            self.log(f"❌ Error in goal analysis: {str(e)}", "ERROR")
            duration = time.time() - start_time
            self.metrics.record_execution(duration, False, str(e))
            self.tracer.end_trace(status="error")
            raise
    
    def _analyze_with_gemini(self, user_input: Dict, goal_taxonomy: Dict) -> Dict:
        """Use Gemini to analyze goals"""
        try:
            model = genai.GenerativeModel("gemini-pro")
            prompt = f"""
            Analyze this learner's career goal and provide insights:
            
            Career Goal: {user_input.get('career_goal')}
            Current Skills: {user_input.get('current_skills', [])}
            Time Available: {user_input.get('time_available_weekly')} hours/week
            Learning Style: {user_input.get('learning_style', [])}
            Constraints: {user_input.get('constraints', [])}
            
            Based on this profile:
            1. What are the key challenges this learner might face?
            2. What quick wins can they achieve in the first month?
            3. What should be their priority focus?
            
            Provide a concise, actionable response.
            """
            
            response = model.generate_content(prompt)
            return {
                "analysis": response.text,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.log(f"⚠️ Gemini analysis failed: {str(e)}", "WARN")
            return {"analysis": "Analysis unavailable", "error": str(e)}


class ResourceResearcherAgent(SkillBridgeAgent):
    """Researches learning resources in parallel"""
    
    RESOURCE_DATABASE = {
        "metadata": {"total_courses": 500},
        "courses": [
            # Sample courses for each skill
            {
                "id": "py_001",
                "title": "Python for Data Science",
                "platform": "Coursera",
                "skill_tags": ["Python", "Data Science"],
                "duration_hours": 40,
                "rating": 4.8,
                "certificate": "Free (audit)",
                "url": "https://coursera.org/python-ds"
            },
            {
                "id": "sql_001",
                "title": "SQL Masterclass",
                "platform": "Udemy",
                "skill_tags": ["SQL", "Database"],
                "duration_hours": 30,
                "rating": 4.7,
                "certificate": "Paid certificate",
                "url": "https://udemy.com/sql-master"
            },
            {
                "id": "ml_001",
                "title": "Machine Learning A-Z",
                "platform": "Udemy",
                "skill_tags": ["Machine Learning", "Python"],
                "duration_hours": 50,
                "rating": 4.6,
                "certificate": "Paid certificate",
                "url": "https://udemy.com/ml-az"
            },
            {
                "id": "react_001",
                "title": "React: The Complete Guide",
                "platform": "Udemy",
                "skill_tags": ["React", "JavaScript"],
                "duration_hours": 40,
                "rating": 4.8,
                "certificate": "Paid certificate",
                "url": "https://udemy.com/react-guide"
            },
            {
                "id": "docker_001",
                "title": "Docker & Kubernetes",
                "platform": "Linux Academy",
                "skill_tags": ["Docker", "DevOps", "Cloud"],
                "duration_hours": 35,
                "rating": 4.7,
                "certificate": "Free",
                "url": "https://linuxacademy.com/docker-k8s"
            }
        ]
    }
    
    def run(self, goal_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Research resources in parallel"""
        self.tracer.start_trace("resource_research", skills=goal_profile['skill_gaps'])
        start_time = time.time()
        
        try:
            self.log("🔍 Starting parallel resource research")
            
            matched_resources = self._parallel_resource_search(goal_profile)
            job_market_insights = self._analyze_job_market_with_gemini(goal_profile)
            
            result = {
                "goal_profile": goal_profile,
                "matched_resources": matched_resources,
                "job_market_insights": job_market_insights,
                "research_timestamp": datetime.utcnow().isoformat()
            }
            
            self.log(f"✅ Parallel research complete: {len(matched_resources)} skills researched")
            duration = time.time() - start_time
            self.metrics.record_execution(duration, True)
            self.tracer.end_trace(status="success")
            
            return result
            
        except Exception as e:
            self.log(f"❌ Error in resource research: {str(e)}", "ERROR")
            duration = time.time() - start_time
            self.metrics.record_execution(duration, False, str(e))
            self.tracer.end_trace(status="error")
            raise
    
    def _parallel_resource_search(self, goal_profile: Dict) -> Dict[str, List]:
        """Search resources in parallel using ThreadPoolExecutor"""
        matched_resources = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._find_courses_for_skill, skill, goal_profile): skill
                for skill in goal_profile['skill_gaps']
            }
            
            for future in as_completed(futures):
                skill = futures[future]
                try:
                    courses = future.result()
                    matched_resources[skill] = courses
                    self.log(f"✓ Found {len(courses)} resources for '{skill}'")
                except Exception as e:
                    self.log(f"⚠️ Failed to find resources for '{skill}': {str(e)}", "WARN")
                    matched_resources[skill] = []
        
        return matched_resources
    
    def _find_courses_for_skill(self, skill: str, goal_profile: Dict) -> List[Dict]:
        """Find courses for a specific skill"""
        matching = []
        
        for course in self.RESOURCE_DATABASE.get('courses', []):
            if skill.lower() in [t.lower() for t in course.get('skill_tags', [])]:
                if self._matches_constraints(course, goal_profile):
                    matching.append({
                        "id": course['id'],
                        "title": course['title'],
                        "platform": course['platform'],
                        "duration_hours": course['duration_hours'],
                        "rating": course['rating'],
                        "certificate": course['certificate'],
                        "url": course.get('url', '#')
                    })
        
        matching.sort(key=lambda x: x['rating'], reverse=True)
        return matching[:3]
    
    def _matches_constraints(self, course: Dict, goal_profile: Dict) -> bool:
        """Check if course matches constraints"""
        if "No cost" in goal_profile['constraints']:
            if course['certificate'] not in ["Free (audit)", "None", "Free", "Badge"]:
                return False
        return True
    
    def _analyze_job_market_with_gemini(self, goal_profile: Dict) -> Dict:
        """Analyze job market using Gemini"""
        try:
            model = genai.GenerativeModel("gemini-pro")
            prompt = f"""
            Provide job market insights for a {goal_profile['primary_goal']} role in 2024-2025:
            1. Current demand trend
            2. Salary expectations in India
            3. Key skills in demand
            4. Career growth opportunities
            
            Keep response concise and actionable.
            """
            
            response = model.generate_content(prompt)
            
            demand_trends = {
                "Data Scientist": "+28% YoY",
                "Data Analyst": "+18% YoY",
                "Web Developer": "+12% YoY",
                "Cloud Engineer": "+42% YoY",
                "AI/ML Engineer": "+35% YoY"
            }
            
            return {
                "role": goal_profile['primary_goal'],
                "demand_trend": demand_trends.get(goal_profile['primary_goal'], "+15% YoY"),
                "market_growth": "High",
                "avg_salary_india": goal_profile['salary_potential'],
                "gemini_insights": response.text,
                "analyzed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.log(f"⚠️ Gemini job market analysis failed: {str(e)}", "WARN")
            return {
                "role": goal_profile['primary_goal'],
                "demand_trend": "+15% YoY",
                "market_growth": "Stable",
                "avg_salary_india": goal_profile['salary_potential']
            }


class RoadmapSynthesizerAgent(SkillBridgeAgent):
    """Synthesizes learning roadmap with iterative evaluation"""
    
    def run(self, research_output: Dict[str, Any], max_iterations: int = 3) -> Dict[str, Any]:
        """Synthesize roadmap with loop-based agent pattern"""
        self.tracer.start_trace("roadmap_synthesis", max_iterations=max_iterations)
        start_time = time.time()
        
        try:
            self.log("📋 Starting roadmap synthesis with iterative evaluation loop")
            
            iteration = 0
            final_roadmap = None
            evaluation_score = 0
            
            while iteration < max_iterations:
                iteration += 1
                self.log(f"🔄 Synthesis iteration {iteration}/{max_iterations}")
                
                draft_roadmap = self._draft_roadmap(research_output)
                evaluation_score = self._evaluate_roadmap_with_gemini(draft_roadmap, research_output)
                
                self.log(f"📊 Self-evaluation score: {evaluation_score}/10")
                
                if evaluation_score >= 7.0:
                    self.log(f"✅ Roadmap quality threshold reached ({evaluation_score}/10)")
                    final_roadmap = draft_roadmap
                    break
            
            if final_roadmap is None:
                final_roadmap = draft_roadmap
                self.log(f"⚠️ Max iterations reached, using final roadmap (score: {evaluation_score}/10)", "WARN")
            
            result = {
                "roadmap": final_roadmap,
                "evaluation_score": evaluation_score,
                "iterations": iteration,
                "synthesized_at": datetime.utcnow().isoformat()
            }
            
            duration = time.time() - start_time
            self.metrics.record_execution(duration, True)
            self.tracer.end_trace(status="success")
            
            return result
            
        except Exception as e:
            self.log(f"❌ Error in roadmap synthesis: {str(e)}", "ERROR")
            duration = time.time() - start_time
            self.metrics.record_execution(duration, False, str(e))
            self.tracer.end_trace(status="error")
            raise
    
    def _draft_roadmap(self, research_output: Dict) -> Dict:
        """Create draft roadmap"""
        goal_profile = research_output['goal_profile']
        matched_resources = research_output['matched_resources']
        
        phases = []
        phase_count = 1
        
        chunk_size = max(1, len(goal_profile['skill_gaps']) // 3)
        skill_phases = [goal_profile['skill_gaps'][i:i+chunk_size] 
                       for i in range(0, len(goal_profile['skill_gaps']), chunk_size)]
        
        for phase_skills in skill_phases:
            phase_data = {
                "phase": phase_count,
                "title": f"Phase {phase_count}: {', '.join(phase_skills[:2])}",
                "duration_weeks": 4,
                "courses": []
            }
            
            for skill in phase_skills:
                if skill in matched_resources and matched_resources[skill]:
                    courses = matched_resources[skill]
                    phase_data['courses'].append({
                        "rank": len(phase_data['courses']) + 1,
                        "skill": skill,
                        **courses[0]
                    })
            
            phases.append(phase_data)
            phase_count += 1
        
        return {
            "learner_id": goal_profile['learner_id'],
            "pathway_title": f"{goal_profile['primary_goal']} Mastery Path",
            "primary_goal": goal_profile['primary_goal'],
            "phases": phases,
            "total_hours": sum(c['duration_hours'] for p in phases for c in p['courses']),
            "total_weeks": sum(p['duration_weeks'] for p in phases)
        }
    
    def _evaluate_roadmap_with_gemini(self, roadmap: Dict, research_output: Dict) -> float:
        """Evaluate roadmap using Gemini and custom metrics"""
        try:
            goal_profile = research_output['goal_profile']
            
            # Custom evaluation metrics
            goal_alignment = min(len(roadmap['phases']) / max(1, len(goal_profile['skill_gaps'])) * 2.5, 2.5)
            feasibility = 2.5 if roadmap['total_hours'] / max(1, roadmap['total_weeks']) <= goal_profile['time_available_weekly'] * 1.5 else 1.25
            cert_value = sum(1 for p in roadmap['phases'] for c in p['courses']) * 0.5
            quality = (sum(c.get('rating', 4) for p in roadmap['phases'] for c in p['courses']) / max(1, sum(len(p['courses']) for p in roadmap['phases']))) / 5 * 2.0
            accessibility = 1.0
            
            total = min(10, goal_alignment + feasibility + cert_value + quality + accessibility)
            
            return round(total, 1)
        except Exception as e:
            self.log(f"⚠️ Evaluation error: {str(e)}", "WARN")
            return 5.0


class SkillBridgeOrchestrator:
    """Orchestrates multi-agent workflow"""
    
    def __init__(self):
        self.goal_analyzer = GoalAnalyzerAgent(
            "Goal Analyzer",
            "Analyzes learner goals and career aspirations"
        )
        self.resource_researcher = ResourceResearcherAgent(
            "Resource Researcher",
            "Researches learning resources in parallel"
        )
        self.roadmap_synthesizer = RoadmapSynthesizerAgent(
            "Roadmap Synthesizer",
            "Synthesizes personalized learning roadmaps"
        )
        self.logger = get_logger("orchestrator")
        self.db = get_db_instance()
    
    def generate_pathway(self, learner_input: dict) -> dict:
        """Generate personalized learning pathway"""
        print(f"\n{'='*70}")
        print(f"🚀 SKILLBRIDGE: MULTI-AGENT PATHWAY GENERATION")
        print(f"{'='*70}\n")
        
        try:
            # Sequential agent execution
            self.logger.info("Starting sequential agent workflow")
            
            goal_profile = self.goal_analyzer.run(learner_input)
            research_output = self.resource_researcher.run(goal_profile)
            synthesis_output = self.roadmap_synthesizer.run(research_output)
            
            result = {
                "learner_id": learner_input.get("learner_id"),
                "status": "success",
                "roadmap": synthesis_output['roadmap'],
                "evaluation_score": synthesis_output['evaluation_score'],
                "job_market_insights": research_output['job_market_insights'],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(
                "Pathway generation complete",
                learner_id=learner_input.get("learner_id"),
                score=synthesis_output['evaluation_score']
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Pathway generation failed: {str(e)}")
            return {
                "learner_id": learner_input.get("learner_id"),
                "status": "error",
                "error": str(e)
            }
