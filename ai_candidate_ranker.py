import logging
from typing import Dict, List, Any, Optional
from candidate_ranker import rank_candidates as base_rank_candidates
from ai_resume_analyzer import ai_analyzer

logger = logging.getLogger(__name__)

def rank_candidates_with_ai(candidates: List[Dict[str, Any]], job_description: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Enhanced candidate ranking that combines traditional scoring with AI analysis.

    Args:
        candidates: List of candidate dictionaries
        job_description: Job description dictionary

    Returns:
        List of ranked candidates with AI insights
    """
    import time
    # First, get base rankings
    base_start = time.time()
    base_rankings = base_rank_candidates(candidates, job_description)
    base_time = time.time() - base_start
    logger.info(f"Base ranking completed in {base_time:.2f} seconds for {len(candidates)} candidates")

    # If AI is not available, return base rankings
    if not ai_analyzer or not ai_analyzer.is_available():
        logger.info("AI analysis not available, using base rankings only")
        return base_rankings

    # Enhance rankings with AI analysis
    enhanced_rankings = []
    ai_start = time.time()

    # Collect candidates that need AI analysis
    candidates_to_analyze = []
    for ranked_candidate in base_rankings:
        candidate = ranked_candidate['candidate']
        if candidate.get('ai_analysis'):
            candidates_to_analyze.append(ranked_candidate)
        else:
            logger.warning(f"No AI analysis found for candidate {candidate.get('name', 'Unknown')}")
            # Still add to rankings without AI
            enhanced_candidate = ranked_candidate.copy()
            enhanced_candidate.update({
                'ai_match_analysis': None,
                'ai_overall_score': 0,
                'traditional_score': ranked_candidate['total_score'],
                'has_ai_analysis': False
            })
            enhanced_rankings.append(enhanced_candidate)

    # Perform AI analysis in parallel
    if candidates_to_analyze:
        import asyncio
        async def analyze_candidates():
            tasks = []
            for ranked_candidate in candidates_to_analyze:
                candidate = ranked_candidate['candidate']
                task = ai_analyzer.analyze_job_match_async(
                    candidate,
                    job_description,
                    candidate.get('ai_analysis', {})
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

        ai_results = asyncio.run(analyze_candidates())

        for i, (ranked_candidate, ai_result) in enumerate(zip(candidates_to_analyze, ai_results)):
            candidate = ranked_candidate['candidate']

            try:
                if isinstance(ai_result, Exception):
                    raise ai_result

                ai_match_analysis = ai_result
                candidate_ai_time = time.time() - ai_start  # Approximate, since parallel
                logger.info(f"AI analysis for {candidate.get('name', 'Unknown')} completed")

                # Combine traditional and AI scores
                enhanced_candidate = ranked_candidate.copy()

                if ai_match_analysis:
                    # Weight the scores: 60% traditional, 40% AI
                    traditional_score = ranked_candidate['total_score']
                    ai_overall_score = ai_match_analysis.get('overall_match_score', 50) / 100.0

                    # Calculate weighted final score
                    final_score = (traditional_score * 0.6) + (ai_overall_score * 0.4)

                    # Update the candidate with AI insights
                    enhanced_candidate.update({
                        'total_score': final_score,
                        'ai_match_analysis': ai_match_analysis,
                        'ai_overall_score': ai_overall_score,
                        'traditional_score': traditional_score,
                        'has_ai_analysis': True
                    })

                    logger.info(f"Enhanced scoring for {candidate.get('name', 'Unknown')}: "
                              f"Traditional={traditional_score:.3f}, AI={ai_overall_score:.3f}, "
                              f"Final={final_score:.3f}")
                else:
                    # No AI analysis available for this candidate
                    enhanced_candidate.update({
                        'ai_match_analysis': None,
                        'ai_overall_score': 0,
                        'traditional_score': ranked_candidate['total_score'],
                        'has_ai_analysis': False
                    })

                enhanced_rankings.append(enhanced_candidate)

            except Exception as e:
                logger.error(f"Error enhancing candidate {candidate.get('name', 'Unknown')} with AI: {e}")
                # Fall back to original ranking
                enhanced_candidate = ranked_candidate.copy()
                enhanced_candidate.update({
                    'ai_match_analysis': None,
                    'ai_overall_score': 0,
                    'traditional_score': ranked_candidate['total_score'],
                    'has_ai_analysis': False
                })
                enhanced_rankings.append(enhanced_candidate)

    ai_total_time = time.time() - ai_start
    logger.info(f"AI enhancement completed in {ai_total_time:.2f} seconds for {len(enhanced_rankings)} candidates")

    # Re-sort by final score
    enhanced_rankings.sort(key=lambda x: x['total_score'], reverse=True)

    # Log final rankings
    logger.info("Final AI-enhanced rankings:")
    for i, candidate in enumerate(enhanced_rankings[:5]):
        name = candidate['candidate'].get('name', 'Unknown')
        score = candidate['total_score']
        has_ai = candidate.get('has_ai_analysis', False)
        logger.info(f"  {i+1}. {name}: {score:.3f} (AI: {'Yes' if has_ai else 'No'})")

    return enhanced_rankings

def get_ai_insights_for_candidate(candidate_data: Dict[str, Any], job_description: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get AI insights for a specific candidate-job combination.
    
    Args:
        candidate_data: Candidate information
        job_description: Job requirements
        
    Returns:
        Dictionary containing AI insights
    """
    if not ai_analyzer or not ai_analyzer.is_available():
        return {
            'available': False,
            'message': 'AI analysis not available. Configure OpenAI API key for enhanced insights.'
        }
    
    try:
        # Get candidate's existing AI analysis
        candidate_ai_analysis = candidate_data.get('ai_analysis', {})
        
        if not candidate_ai_analysis:
            return {
                'available': False,
                'message': 'No AI analysis found for this candidate. Re-upload their resume for AI insights.'
            }
        
        # Perform job-specific matching
        job_match_analysis = ai_analyzer.analyze_job_match(
            candidate_data, 
            job_description, 
            candidate_ai_analysis
        )
        
        return {
            'available': True,
            'candidate_analysis': candidate_ai_analysis,
            'job_match_analysis': job_match_analysis,
            'insights': {
                'strengths': job_match_analysis.get('key_strengths_for_role', []),
                'concerns': job_match_analysis.get('potential_concerns', []),
                'missing_skills': job_match_analysis.get('missing_skills', []),
                'recommendations': job_match_analysis.get('development_recommendations', []),
                'hiring_recommendation': job_match_analysis.get('hiring_recommendation', 'consider'),
                'interview_focus': job_match_analysis.get('interview_focus_areas', []),
                'onboarding_suggestions': job_match_analysis.get('onboarding_suggestions', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        return {
            'available': False,
            'message': f'Error generating AI insights: {str(e)}'
        }

def get_candidate_quality_insights(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get quality insights for a candidate from their AI analysis.
    
    Args:
        candidate_data: Candidate information
        
    Returns:
        Dictionary containing quality insights
    """
    ai_analysis = candidate_data.get('ai_analysis', {})
    
    if not ai_analysis:
        return {
            'available': False,
            'message': 'No AI analysis available for this candidate.'
        }
    
    return {
        'available': True,
        'quality_score': ai_analysis.get('overall_quality_score', 0),
        'professional_summary': ai_analysis.get('professional_summary', ''),
        'key_strengths': ai_analysis.get('key_strengths', []),
        'areas_for_improvement': ai_analysis.get('areas_for_improvement', []),
        'career_progression': ai_analysis.get('career_progression', ''),
        'technical_level': ai_analysis.get('technical_expertise_level', 'unknown'),
        'leadership_potential': ai_analysis.get('leadership_potential', ''),
        'recommended_roles': ai_analysis.get('recommended_roles', []),
        'salary_estimate': ai_analysis.get('salary_range_estimate', ''),
        'red_flags': ai_analysis.get('red_flags', [])
    }

def batch_analyze_candidates_for_job(candidates: List[Dict[str, Any]], 
                                   job_description: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform batch AI analysis for multiple candidates against a job.
    
    Args:
        candidates: List of candidates
        job_description: Job requirements
        
    Returns:
        Dictionary containing batch analysis results
    """
    if not ai_analyzer or not ai_analyzer.is_available():
        return {
            'available': False,
            'message': 'AI analysis not available'
        }
    
    results = {
        'available': True,
        'job_title': job_description.get('title', 'Unknown'),
        'total_candidates': len(candidates),
        'analyzed_candidates': 0,
        'top_recommendations': [],
        'skill_gap_analysis': {},
        'hiring_recommendations': {
            'strong_recommend': 0,
            'recommend': 0,
            'consider': 0,
            'not_recommend': 0
        }
    }
    
    try:
        # Analyze each candidate
        candidate_analyses = []
        
        for candidate in candidates:
            if candidate.get('ai_analysis'):
                job_match = ai_analyzer.analyze_job_match(
                    candidate, 
                    job_description, 
                    candidate.get('ai_analysis', {})
                )
                
                candidate_analyses.append({
                    'candidate': candidate,
                    'job_match': job_match
                })
                
                # Update hiring recommendation counts
                recommendation = job_match.get('hiring_recommendation', 'consider')
                if recommendation in results['hiring_recommendations']:
                    results['hiring_recommendations'][recommendation] += 1
                
                results['analyzed_candidates'] += 1
        
        # Sort by overall match score
        candidate_analyses.sort(
            key=lambda x: x['job_match'].get('overall_match_score', 0), 
            reverse=True
        )
        
        # Get top 5 recommendations
        results['top_recommendations'] = [
            {
                'name': analysis['candidate'].get('name', 'Unknown'),
                'match_score': analysis['job_match'].get('overall_match_score', 0),
                'key_strengths': analysis['job_match'].get('key_strengths_for_role', [])[:3],
                'hiring_recommendation': analysis['job_match'].get('hiring_recommendation', 'consider')
            }
            for analysis in candidate_analyses[:5]
        ]
        
        # Analyze skill gaps across all candidates
        all_missing_skills = []
        for analysis in candidate_analyses:
            missing_skills = analysis['job_match'].get('missing_skills', [])
            all_missing_skills.extend(missing_skills)
        
        # Count frequency of missing skills
        skill_counts = {}
        for skill in all_missing_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Get most common missing skills
        results['skill_gap_analysis'] = dict(
            sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        results['available'] = False
        results['message'] = f'Batch analysis failed: {str(e)}'
        return results