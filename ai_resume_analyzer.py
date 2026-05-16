import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class AIResumeAnalyzer:
    """Advanced AI-powered resume analyzer using OpenAI GPT models."""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API key not configured. AI analysis will be disabled.")
            return
        
        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.client is not None
    
    def analyze_resume_comprehensive(self, resume_text: str, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of a resume.
        
        Args:
            resume_text: Raw text extracted from resume
            candidate_data: Parsed candidate data
            
        Returns:
            Dictionary containing AI analysis results
        """
        if not self.is_available():
            return self._fallback_analysis(candidate_data)
        
        try:
            prompt = self._create_resume_analysis_prompt(resume_text, candidate_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional and resume analyst with deep knowledge of various industries and job requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_ai_analysis(analysis_text, candidate_data)
            
        except Exception as e:
            logger.error(f"AI resume analysis failed: {e}")
            return self._fallback_analysis(candidate_data)
    
    def analyze_job_match(self, candidate_data: Dict[str, Any], job_description: Dict[str, Any],
                         candidate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how well a candidate matches a specific job using AI.

        Args:
            candidate_data: Candidate information
            job_description: Job requirements
            candidate_analysis: Previous AI analysis of candidate

        Returns:
            Dictionary containing match analysis and scoring
        """
        if not self.is_available():
            return self._fallback_job_match(candidate_data, job_description)

        try:
            prompt = self._create_job_match_prompt(candidate_data, job_description, candidate_analysis)
            logger.info(f"AI job match prompt length: {len(prompt)} characters for candidate {candidate_data.get('name', 'Unknown')}")

            import time
            api_start = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional specializing in candidate-job matching and hiring decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            api_time = time.time() - api_start
            logger.info(f"OpenAI API call for job match took {api_time:.2f} seconds for candidate {candidate_data.get('name', 'Unknown')}")

            match_text = response.choices[0].message.content
            return self._parse_job_match_analysis(match_text, candidate_data, job_description)

        except Exception as e:
            logger.error(f"AI job match analysis failed: {e}")
            return self._fallback_job_match(candidate_data, job_description)

    async def analyze_job_match_async(self, candidate_data: Dict[str, Any], job_description: Dict[str, Any],
                                     candidate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async version of analyze_job_match for parallel processing.
        """
        if not self.is_available():
            return self._fallback_job_match(candidate_data, job_description)

        try:
            prompt = self._create_job_match_prompt(candidate_data, job_description, candidate_analysis)
            logger.info(f"AI job match prompt length: {len(prompt)} characters for candidate {candidate_data.get('name', 'Unknown')}")

            import time
            api_start = time.time()
            response = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional specializing in candidate-job matching and hiring decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            api_time = time.time() - api_start
            logger.info(f"OpenAI API call for job match took {api_time:.2f} seconds for candidate {candidate_data.get('name', 'Unknown')}")

            match_text = response.choices[0].message.content
            return self._parse_job_match_analysis(match_text, candidate_data, job_description)

        except Exception as e:
            logger.error(f"AI job match analysis failed: {e}")
            return self._fallback_job_match(candidate_data, job_description)
    
    def generate_candidate_summary(self, candidate_data: Dict[str, Any], 
                                 candidate_analysis: Dict[str, Any]) -> str:
        """Generate a professional summary of the candidate."""
        if not self.is_available():
            return self._fallback_summary(candidate_data)
        
        try:
            prompt = f"""
            Create a concise, professional summary (2-3 sentences) for this candidate based on their profile:
            
            Name: {candidate_data.get('name', 'Unknown')}
            Experience: {candidate_data.get('experience_years', 0)} years
            Skills: {', '.join(candidate_data.get('skills', [])[:10])}
            Education: {self._format_education_for_prompt(candidate_data.get('education', []))}
            
            Key Strengths: {', '.join(candidate_analysis.get('key_strengths', [])[:5])}
            
            Focus on their most relevant qualifications and potential value to employers.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional writing candidate summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return self._fallback_summary(candidate_data)
    
    def _create_resume_analysis_prompt(self, resume_text: str, candidate_data: Dict[str, Any]) -> str:
        """Create prompt for comprehensive resume analysis."""
        return f"""
        Analyze this resume comprehensively and provide insights in JSON format:

        RESUME TEXT:
        {resume_text[:3000]}  # Limit text to avoid token limits

        PARSED DATA:
        Name: {candidate_data.get('name', 'Unknown')}
        Experience: {candidate_data.get('experience_years', 0)} years
        Skills: {', '.join(candidate_data.get('skills', []))}
        Education: {self._format_education_for_prompt(candidate_data.get('education', []))}

        Please provide analysis in this JSON structure:
        {{
            "professional_summary": "2-3 sentence summary of the candidate",
            "key_strengths": ["strength1", "strength2", "strength3"],
            "areas_for_improvement": ["area1", "area2"],
            "career_progression": "assessment of career growth and trajectory",
            "technical_expertise_level": "junior/mid/senior/expert",
            "leadership_potential": "assessment of leadership qualities",
            "cultural_fit_indicators": ["indicator1", "indicator2"],
            "red_flags": ["flag1", "flag2"] or [],
            "overall_quality_score": 85,
            "recommended_roles": ["role1", "role2", "role3"],
            "salary_range_estimate": "estimated salary range based on experience and skills"
        }}

        Be objective, professional, and focus on factual observations from the resume.
        """
    
    def _create_job_match_prompt(self, candidate_data: Dict[str, Any], 
                               job_description: Dict[str, Any], 
                               candidate_analysis: Dict[str, Any]) -> str:
        """Create prompt for job matching analysis."""
        return f"""
        Analyze how well this candidate matches the job requirements:

        CANDIDATE:
        Name: {candidate_data.get('name', 'Unknown')}
        Experience: {candidate_data.get('experience_years', 0)} years
        Skills: {', '.join(candidate_data.get('skills', []))}
        Education: {self._format_education_for_prompt(candidate_data.get('education', []))}
        Key Strengths: {', '.join(candidate_analysis.get('key_strengths', []))}
        Technical Level: {candidate_analysis.get('technical_expertise_level', 'Unknown')}

        JOB REQUIREMENTS:
        Title: {job_description.get('title', 'Unknown')}
        Required Skills: {', '.join(job_description.get('required_skills', []))}
        Min Experience: {job_description.get('min_experience', 0)} years
        Required Education: {self._format_education_for_prompt(job_description.get('required_education', []))}

        Provide analysis in this JSON structure:
        {{
            "overall_match_score": 85,
            "skills_match_score": 90,
            "experience_match_score": 80,
            "education_match_score": 85,
            "cultural_fit_score": 75,
            "detailed_explanation": "Comprehensive explanation of the match assessment",
            "key_strengths_for_role": ["strength1", "strength2", "strength3"],
            "potential_concerns": ["concern1", "concern2"],
            "missing_skills": ["skill1", "skill2"],
            "development_recommendations": ["recommendation1", "recommendation2"],
            "hiring_recommendation": "strong_recommend/recommend/consider/not_recommend",
            "interview_focus_areas": ["area1", "area2", "area3"],
            "onboarding_suggestions": ["suggestion1", "suggestion2"]
        }}

        Scores should be 0-100. Be thorough and provide actionable insights.
        """
    
    def _parse_ai_analysis(self, analysis_text: str, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI analysis response into structured data."""
        try:
            # Try to extract JSON from the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Validate and clean the analysis
                return self._validate_analysis_data(analysis, candidate_data)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {e}")
            return self._fallback_analysis(candidate_data)
    
    def _parse_job_match_analysis(self, match_text: str, candidate_data: Dict[str, Any], 
                                job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Parse job match analysis response."""
        try:
            start_idx = match_text.find('{')
            end_idx = match_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = match_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                return self._validate_match_data(analysis, candidate_data, job_description)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse job match analysis: {e}")
            return self._fallback_job_match(candidate_data, job_description)
    
    def _validate_analysis_data(self, analysis: Dict[str, Any], 
                              candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis data."""
        validated = {
            "professional_summary": analysis.get("professional_summary", "No summary available"),
            "key_strengths": analysis.get("key_strengths", [])[:5],
            "areas_for_improvement": analysis.get("areas_for_improvement", [])[:3],
            "career_progression": analysis.get("career_progression", "Unable to assess"),
            "technical_expertise_level": analysis.get("technical_expertise_level", "unknown"),
            "leadership_potential": analysis.get("leadership_potential", "Unable to assess"),
            "cultural_fit_indicators": analysis.get("cultural_fit_indicators", [])[:3],
            "red_flags": analysis.get("red_flags", [])[:3],
            "overall_quality_score": max(0, min(100, analysis.get("overall_quality_score", 50))),
            "recommended_roles": analysis.get("recommended_roles", [])[:5],
            "salary_range_estimate": analysis.get("salary_range_estimate", "Unable to estimate")
        }
        
        return validated
    
    def _validate_match_data(self, analysis: Dict[str, Any], candidate_data: Dict[str, Any], 
                           job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean match analysis data."""
        validated = {
            "overall_match_score": max(0, min(100, analysis.get("overall_match_score", 50))),
            "skills_match_score": max(0, min(100, analysis.get("skills_match_score", 50))),
            "experience_match_score": max(0, min(100, analysis.get("experience_match_score", 50))),
            "education_match_score": max(0, min(100, analysis.get("education_match_score", 50))),
            "cultural_fit_score": max(0, min(100, analysis.get("cultural_fit_score", 50))),
            "detailed_explanation": analysis.get("detailed_explanation", "No detailed explanation available"),
            "key_strengths_for_role": analysis.get("key_strengths_for_role", [])[:5],
            "potential_concerns": analysis.get("potential_concerns", [])[:3],
            "missing_skills": analysis.get("missing_skills", [])[:5],
            "development_recommendations": analysis.get("development_recommendations", [])[:3],
            "hiring_recommendation": analysis.get("hiring_recommendation", "consider"),
            "interview_focus_areas": analysis.get("interview_focus_areas", [])[:5],
            "onboarding_suggestions": analysis.get("onboarding_suggestions", [])[:3]
        }
        
        return validated
    
    def _format_education_for_prompt(self, education: List[Dict[str, Any]]) -> str:
        """Format education data for prompts."""
        if not education:
            return "No education information"
        
        formatted = []
        for edu in education[:3]:  # Limit to top 3
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                university = edu.get('university', '')
                year = edu.get('year', '')
                
                edu_str = degree
                if field:
                    edu_str += f" in {field}"
                if university:
                    edu_str += f" from {university}"
                if year:
                    edu_str += f" ({year})"
                    
                formatted.append(edu_str)
            else:
                formatted.append(str(edu))
        
        return '; '.join(formatted)
    
    def _fallback_analysis(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis when AI is not available."""
        skills_count = len(candidate_data.get('skills', []))
        experience_years = candidate_data.get('experience_years', 0)
        
        # Simple heuristic scoring
        quality_score = min(100, 30 + (skills_count * 5) + (experience_years * 3))
        
        return {
            "professional_summary": f"Candidate with {experience_years} years of experience and {skills_count} listed skills.",
            "key_strengths": candidate_data.get('skills', [])[:3],
            "areas_for_improvement": ["AI analysis not available"],
            "career_progression": "Unable to assess without AI analysis",
            "technical_expertise_level": "junior" if experience_years < 3 else "mid" if experience_years < 7 else "senior",
            "leadership_potential": "Unable to assess without AI analysis",
            "cultural_fit_indicators": [],
            "red_flags": [],
            "overall_quality_score": quality_score,
            "recommended_roles": [],
            "salary_range_estimate": "Unable to estimate without AI analysis"
        }
    
    def _fallback_job_match(self, candidate_data: Dict[str, Any], 
                          job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback job match analysis."""
        return {
            "overall_match_score": 50,
            "skills_match_score": 50,
            "experience_match_score": 50,
            "education_match_score": 50,
            "cultural_fit_score": 50,
            "detailed_explanation": "AI analysis not available. Please configure OpenAI API key for detailed matching.",
            "key_strengths_for_role": [],
            "potential_concerns": ["AI analysis not available"],
            "missing_skills": [],
            "development_recommendations": [],
            "hiring_recommendation": "consider",
            "interview_focus_areas": [],
            "onboarding_suggestions": []
        }
    
    def _fallback_summary(self, candidate_data: Dict[str, Any]) -> str:
        """Provide fallback summary when AI is not available."""
        name = candidate_data.get('name', 'Candidate')
        experience = candidate_data.get('experience_years', 0)
        skills_count = len(candidate_data.get('skills', []))
        
        return f"{name} is a professional with {experience} years of experience and {skills_count} technical skills."

# Global instance
ai_analyzer = AIResumeAnalyzer()