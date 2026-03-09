#!/usr/bin/env python3
"""
Migration script to add database indexes for recommendation query optimization.

This script adds indexes to support the optimized For You section queries:
- Profile table indexes for user_id and education_level filtering
- Opportunity table indexes for eligibility and location_type filtering
- Composite indexes for common query patterns

Run this script after updating the model definitions to ensure
existing databases have the proper indexes for optimal performance.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_indexes():
    """Add database indexes for recommendation query optimization."""
    db = SessionLocal()
    
    try:
        logger.info("🚀 Adding recommendation optimization indexes...")
        
        # Profile table indexes
        profile_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_education_level ON profiles(education_level)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_user_education ON profiles(user_id, education_level)"
        ]
        
        # Opportunity table indexes
        opportunity_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_opportunities_eligibility ON opportunities(eligibility)",
            "CREATE INDEX IF NOT EXISTS idx_opportunities_location_type ON opportunities(location_type)",
            "CREATE INDEX IF NOT EXISTS idx_opportunities_active_deadline ON opportunities(status, deadline)"
        ]
        
        # Add profile indexes
        logger.info("Adding Profile table indexes...")
        for index_sql in profile_indexes:
            try:
                db.execute(text(index_sql))
                logger.info(f"✅ Added index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except Exception as e:
                logger.warning(f"⚠️ Index might already exist: {e}")
        
        # Add opportunity indexes
        logger.info("Adding Opportunity table indexes...")
        for index_sql in opportunity_indexes:
            try:
                db.execute(text(index_sql))
                logger.info(f"✅ Added index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except Exception as e:
                logger.warning(f"⚠️ Index might already exist: {e}")
        
        # Commit changes
        db.commit()
        logger.info("✨ All recommendation optimization indexes added successfully!")
        
        # Analyze tables for query planner optimization
        logger.info("Analyzing tables for query optimization...")
        try:
            db.execute(text("ANALYZE profiles"))
            db.execute(text("ANALYZE opportunities"))
            db.commit()
            logger.info("✅ Table analysis completed")
        except Exception as e:
            logger.warning(f"⚠️ Table analysis failed (might not be supported): {e}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_indexes():
    """Verify that the indexes were created successfully."""
    db = SessionLocal()
    
    try:
        logger.info("🔍 Verifying indexes...")
        
        # Check PostgreSQL indexes
        try:
            result = db.execute(text("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename IN ('profiles', 'opportunities')
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """))
            
            indexes = result.fetchall()
            logger.info(f"Found {len(indexes)} indexes:")
            for index in indexes:
                logger.info(f"  📊 {index.tablename}.{index.indexname}")
                
        except Exception:
            # Fallback for SQLite or other databases
            logger.info("Using generic index verification...")
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"))
            indexes = result.fetchall()
            logger.info(f"Found {len(indexes)} indexes:")
            for index in indexes:
                logger.info(f"  📊 {index.name}")
        
    except Exception as e:
        logger.error(f"❌ Index verification failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("RECOMMENDATION OPTIMIZATION INDEX MIGRATION")
    logger.info("=" * 60)
    
    try:
        add_indexes()
        verify_indexes()
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        sys.exit(1)